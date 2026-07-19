# CSS 命名规则体系

> 本文档定义一套完整的 CSS 命名规则体系，重点解决深度嵌套 DOM 元素的命名问题。基于 BEM 方法论，参考 Element Plus 组件库的命名实践，确保命名清晰反映 DOM 结构关系，同时保持可维护性和扩展性。

---

## 目录

- [一、CSS 命名的核心原则与设计理念](#一css-命名的核心原则与设计理念)
- [二、深度嵌套 DOM 元素的命名策略](#二深度嵌套-dom-元素的命名策略)
- [三、元素间层级关系在命名中的体现](#三元素间层级关系在命名中的体现)
- [四、与 Element Plus 命名规则的对比分析](#四与-element-plus-命名规则的对比分析)
- [五、实际应用示例](#五实际应用示例)
- [六、命名规则使用规范与注意事项](#六命名规则使用规范与注意事项)
- [附录：命名速查表](#附录命名速查表)

---

## 一、CSS 命名的核心原则与设计理念

### 1.1 为什么需要 CSS 命名规则？

在小项目中，自由命名可以工作。但中大型项目面临的核心问题：

| 问题 | 表现 | 影响 |
|------|------|------|
| 样式污染 | 同名类相互覆盖 | 难以排查的 UI 异常 |
| 层级混乱 | 深度嵌套选择器导致优先级失控 | 修改样式需要不断加 `!important` |
| 可读性差 | `.box .inner .item .txt` 无法理解结构 | 维护成本高，新人难上手 |
| 重构困难 | 修改 DOM 结构导致样式失效 | 不敢动原有代码 |

**CSS 命名规则的本质：用类名建立代码契约，让单个类名即能表达完整的语义信息。**

### 1.2 核心设计理念

**理念一：语义化优先于视觉化**

```
❌ .red-text、.big-box、.left-menu
✅ .text--danger、.card--large、.sidebar
```

名称应表达"是什么"而非"长什么样"。颜色、尺寸会变，语义不会。

**理念二：扁平化优于嵌套化**

```
❌ .card__body__list__item__title  （深层嵌套）
✅ .card__title                     （扁平命名）
```

深层嵌套的 BEM 类名是设计缺陷的信号。元素应直接挂载到 Block 下，形成扁平结构。

**理念三：组件化即模块化**

```
❌ .page-home .header .nav .item
✅ .nav-bar__item
```

每个独立的 UI 单元应是一个 Block，其类名不应依赖父级上下文。

**理念四：可预测性**

```
✅ .button--disabled  → 一看就知道是禁用态按钮
❌ .btn-v2-new        → 无法理解含义
```

看到类名就能预测其对应的 DOM 结构和行为。

---

## 二、深度嵌套 DOM 元素的命名策略

### 2.1 核心问题：嵌套深度与命名层级的关系

**问题场景：** 当一个组件的 DOM 结构超过 3 层嵌套时，是否需要通过命名来体现层级关系？

```
<!-- 深层嵌套的 DOM -->
<div class="table">
  <div class="table__header">
    <div class="table__header-row">
      <div class="table__header-cell">
        <div class="table__header-cell-sort-icon">
          <span class="table__header-cell-sort-icon-arrow"></span>
        </div>
      </div>
    </div>
  </div>
</div>
```

**答案：不需要通过命名嵌套来体现 DOM 层级，正确的做法是扁平命名。**

### 2.2 扁平命名法：推荐方案

**核心规则：所有 Element 都是 Block 的直接子级，在命名层面不体现 DOM 深度。**

```
<!-- 5 层 DOM 嵌套，但命名全部扁平挂载到 Block 下 -->
<div class="table">
  <div class="table__header">
    <div class="table__row">
      <div class="table__cell">
        <div class="table__sort-icon">
          <span class="table__sort-arrow"></span>
        </div>
      </div>
    </div>
  </div>
</div>
```

**扁平命名的 CSS：**

```css
.table { }
.table__header { }
.table__row { }
.table__cell { }
.table__sort-icon { }
.table__sort-arrow { }
```

**为什么扁平命名是正确的？**

| 错误的嵌套命名 | 问题 |
|---------------|------|
| `.table__header__row__cell` | 类名过长，DOM 结构调整时全部失效 |
| `.table .header .row .cell` | 后代选择器导致优先级不可控 |
| `.table__header-row-cell` | 把结构层级硬编码到单词语义中 |

**扁平命名的优势：**
- 类名短，可读性高
- DOM 结构调整不影响类名有效性
- 选择器优先级始终一致（单类名）
- 每个 Element 平等地属于 Block，不依赖兄弟元素

### 2.3 何时需要引入子 Block？

当某个 DOM 部分满足以下条件时，应将其提升为独立 Block：

1. **可复用性**：该部分在多个不同的 Block 中使用
2. **语义独立性**：该部分有独立的业务含义
3. **复杂度**：该部分内部有 3 个以上子元素

```
<!-- 反例：将按钮作为 card 的子元素 -->
<div class="card">
  <button class="card__button">提交</button>     <!-- ❌ 按钮不是 card 独有的 -->
</div>

<!-- 正例：按钮是独立 Block -->
<div class="card">
  <button class="button button--primary">提交</button>  <!-- ✅ -->
</div>
```

**判断标准：**

```
这个元素是否只在当前 Block 中存在？
├── 是 → 作为 Block 的 Element
└── 否 → 提升为独立 Block，通过组合方式使用
```

### 2.4 命名深度对照表

| DOM 层级 | 错误命名 | 正确命名 | 策略 |
|----------|---------|---------|------|
| 1 层 | `.card` | `.card` | Block |
| 2 层 | `.card__title` | `.card__title` | Element |
| 3 层 | `.card__body__text` | `.card__body` + `.card__text` | 扁平为 2 个 Element |
| 4 层 | `.card__body__list__item` | `.card__list-item` | 合并语义或提升为 Block |
| 5+ 层 | `.card__body__list__item__meta` | `.list-item`（独立 Block） | 提升为独立 Block |

---

## 三、元素间层级关系在命名中的体现

### 3.1 通过 Block 边界体现层级

DOM 层级关系通过**组件边界（Block 边界）**来体现，而非通过命名嵌套。

```
<!-- 层级关系通过 HTML 结构体现，命名保持扁平 -->
<div class="page">                           <!-- Block: page -->
  <aside class="sidebar">                    <!-- Block: sidebar -->
    <nav class="menu">                       <!-- Block: menu -->
      <div class="menu__item">               <!-- Element: menu__item -->
        <span class="menu__label"></span>     <!-- Element: menu__label -->
      </div>
    </nav>
  </aside>
  <main class="content">                     <!-- Block: content -->
    <div class="card">                       <!-- Block: card -->
      <h2 class="card__title"></h2>          <!-- Element: card__title -->
      <p class="card__text"></p>             <!-- Element: card__text -->
    </div>
  </main>
</div>
```

**关键洞察：** 每个 Block 是独立的命名空间。`.menu__item` 和 `.card__title` 各自属于不同的 Block，互不干扰。HTML 的嵌套关系已经表达了层级，CSS 命名不需要再次重复。

### 3.2 通过 Block 后缀表达变体关系

Element Plus 的 `blockSuffix` 机制用于表达语义相关的 Block 变体：

```css
/* 同一组件的不同语义变体 */
.el-button           /* 基础按钮 */
.el-button-group     /* 按钮组 */
.el-input            /* 基础输入框 */
.el-input-group      /* 输入框组 */
.el-input-number     /* 数字输入框 */
```

**适用场景：** 当两个 Block 具有强语义关联但结构不同时，使用 `{prefix}-{block}-{suffix}` 模式。

### 3.3 通过 CSS 变量（自定义属性）体现继承关系

对于需要跨层级传递的样式值（如颜色、间距），使用 CSS 变量而非命名：

```css
.card {
  --card-padding: 16px;
  --card-radius: 8px;
  --card-bg: #fff;
  padding: var(--card-padding);
  border-radius: var(--card-radius);
  background: var(--card-bg);
}

.card__header {
  padding: var(--card-padding);
  border-bottom: 1px solid #eee;
}

.card__footer {
  padding: var(--card-padding);
  border-top: 1px solid #eee;
}
```

---

## 四、与 Element Plus 命名规则的对比分析

### 4.1 Element Plus 命名体系剖析

Element Plus 采用**带命名空间前缀的 BEM 规范**，核心实现位于 `useNamespace` 钩子。

**命名结构：**

```
{namespace}-{block}[{-blockSuffix}][__{element}][--{modifier}]
```

**命名空间（Namespace）：** `el`

| 类别 | 格式 | 示例 |
|------|------|------|
| Block | `el-{block}` | `el-button`、`el-input`、`el-dialog` |
| Block 变体 | `el-{block}-{suffix}` | `el-button-group`、`el-input-number` |
| Element | `el-{block}__{element}` | `el-button__icon`、`el-input__inner` |
| Modifier | `el-{block}--{modifier}` | `el-button--primary`、`el-input--large` |
| Element Modifier | `el-{block}__{element}--{modifier}` | `el-button__icon--loading` |
| BlockSuffix Element | `el-{block}-{suffix}__{element}` | `el-button-group__item` |
| 状态类 | `is-{state}` | `is-disabled`、`is-loading`、`is-active` |

### 4.2 Element Plus 命名生成函数

```typescript
// Element Plus 源码 useNamespace 核心逻辑
const _bem = (
  namespace: string,   // 命名空间，如 'el'
  block: string,       // 块名，如 'button'
  blockSuffix: string, // 块后缀，如 'group'
  element: string,     // 元素名，如 'icon'
  modifier: string     // 修饰符，如 'primary'
) => {
  let cls = `${namespace}-${block}`
  if (blockSuffix) cls += `-${blockSuffix}`
  if (element) cls += `__${element}`
  if (modifier) cls += `--${modifier}`
  return cls
}

// 使用示例
_bem('el', 'button', '', 'icon', '')          // 'el-button__icon'
_bem('el', 'button', 'group', 'item', '')     // 'el-button-group__item'
_bem('el', 'button', '', '', 'primary')       // 'el-button--primary'
```

### 4.3 Element Plus 处理深度嵌套的策略

Element Plus 在遇到深层 DOM 结构时，采用**扁平 Element 命名**策略：

```
el-table 组件结构：
el-table
├── el-table__header-wrapper
│   └── el-table__header
│       └── el-table__cell              ← 不写 el-table__header__cell
├── el-table__body-wrapper
│   └── el-table__body
│       └── el-table__row
│           └── el-table__cell          ← 不写 el-table__body__row__cell
└── el-table__footer-wrapper

el-dialog 组件结构：
el-dialog
├── el-dialog__header
│   ├── el-dialog__title
│   └── el-dialog__headerbtn           ← 扁平命名，不写 el-dialog__header__btn
├── el-dialog__body
└── el-dialog__footer
```

**关键策略：**
- 所有 Element 直接挂载到 Block 命名空间下
- 不通过命名表达 DOM 层级深度
- 使用语义化后缀区分不同层级的同类型元素（如 `headerbtn` 而非 `header__btn`）

### 4.4 Element Plus 的 `is-` 状态前缀

Element Plus 使用 `is-` 前缀表达动态状态，这与 BEM 的 `--modifier` 互补：

| 用途 | 格式 | 示例 |
|------|------|------|
| 静态变体 | `--modifier` | `el-button--primary`、`el-button--large` |
| 动态状态 | `is-{state}` | `is-disabled`、`is-loading`、`is-active` |

```html
<!-- 静态变体 + 动态状态组合 -->
<button class="el-button el-button--primary is-loading is-disabled">
  提交
</button>
```

### 4.5 我们采纳的规则与改进

| 维度 | Element Plus 做法 | 我们的规则 | 理由 |
|------|------------------|-----------|------|
| 命名空间 | `el-` 前缀 | `app-` 前缀（推荐） | 与第三方库区分，避免冲突 |
| 分隔符 | `__` 和 `--` | `__` 和 `--` | 与 BEM 标准一致 |
| 状态前缀 | `is-` | `is-` | 与 Element Plus 一致 |
| 深度嵌套 | 扁平命名 | 扁平命名 + 子 Block 提升 | 增加子 Block 提升规则 |
| SCSS 嵌套 | `@mixin b/e/m` + `@at-root` | `@mixin b/e/m` + `@at-root` | 与 Element Plus 源码一致 |
| CSS 变量 | `--el-{name}` | `--app-{block}-{name}` | 按组件作用域区分 |

---

## 五、实际应用示例

### 5.1 基础组件命名

```html
<!-- 按钮组件 -->
<button class="app-button app-button--primary app-button--large">
  <span class="app-button__icon"></span>
  <span class="app-button__text">提交</span>
</button>
```

```scss
// 使用 SCSS Mixin 编写
@include b(button) {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;

  @include e(icon) {
    margin-right: 8px;
    width: 16px;
    height: 16px;
  }

  @include e(text) {
    font-size: 14px;
  }

  @include m(primary) {
    background: #1890ff;
    color: #fff;
  }

  @include m(large) {
    padding: 12px 24px;
    font-size: 16px;
  }
}
```

### 5.2 卡片组件（3 层嵌套）

```html
<!-- 卡片组件 —— 3 层 DOM 嵌套，全部扁平命名 -->
<div class="app-card">
  <div class="app-card__header">
    <h3 class="app-card__title">卡片标题</h3>
    <span class="app-card__subtitle">副标题</span>
  </div>
  <div class="app-card__cover">
    <img class="app-card__image" src="..." alt="" />
  </div>
  <div class="app-card__body">
    <p class="app-card__text">卡片内容描述</p>
  </div>
  <div class="app-card__footer">
    <button class="app-button app-button--primary">操作</button>
  </div>
</div>
```

```scss
@include b(card) {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;

  @include e(header) { padding: 16px 20px; }
  @include e(title) { font-size: 18px; margin: 0; }
  @include e(subtitle) { font-size: 12px; color: #999; }
  @include e(cover) { width: 100%; }
  @include e(image) { width: 100%; display: block; }
  @include e(body) { padding: 16px 20px; }
  @include e(text) { color: #666; line-height: 1.6; }
  @include e(footer) { padding: 12px 20px; border-top: 1px solid #eee; }
}
```

### 5.3 表格组件（5 层嵌套 + 子 Block 提升）

```html
<!-- 表格 —— 错综复杂的 DOM 结构 -->
<div class="app-table">
  <!-- 表头区域 -->
  <div class="app-table__header">
    <div class="app-table__row">
      <div class="app-table__cell app-table__cell--header">
        <span class="app-table__label">名称</span>
        <span class="app-table__sort-icon app-table__sort-icon--asc"></span>
      </div>
      <div class="app-table__cell app-table__cell--header">
        <span class="app-table__label">状态</span>
      </div>
    </div>
  </div>

  <!-- 表体区域 -->
  <div class="app-table__body">
    <div class="app-table__row">
      <div class="app-table__cell">
        <span class="app-table__cell-text">项目 A</span>
      </div>
      <div class="app-table__cell">
        <!-- 状态标签提升为独立 Block -->
        <span class="app-tag app-tag--success">进行中</span>
      </div>
    </div>
  </div>

  <!-- 空状态 -->
  <div class="app-table__empty">
    <p class="app-table__empty-text">暂无数据</p>
  </div>

  <!-- 分页区域 —— 提升为独立 Block -->
  <div class="app-table__footer">
    <div class="app-pagination">
      <button class="app-pagination__prev">上一页</button>
      <span class="app-pagination__current">1</span>
      <button class="app-pagination__next">下一页</button>
    </div>
  </div>
</div>
```

```scss
@include b(table) {
  width: 100%;
  border-collapse: collapse;

  @include e(header) { border-bottom: 2px solid #eee; }
  @include e(body) { }
  @include e(row) { display: flex; border-bottom: 1px solid #f5f5f5; }
  @include e(cell) {
    flex: 1;
    padding: 12px 16px;
    @include m(header) {
      font-weight: bold;
      background: #fafafa;
    }
  }
  @include e(label) { }
  @include e(sort-icon) {
    display: inline-block;
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    @include m(asc) { border-bottom: 6px solid #999; }
    @include m(desc) { border-top: 6px solid #999; }
  }
  @include e(cell-text) { }
  @include e(empty) {
    padding: 60px 0;
    text-align: center;
  }
  @include e(empty-text) { color: #999; }
  @include e(footer) { padding: 16px; display: flex; justify-content: flex-end; }
}
```

### 5.4 表单组件（多层嵌套 + 复杂布局）

```html
<!-- 表单 —— 嵌套层级深但命名扁平 -->
<div class="app-form">
  <div class="app-form__item">
    <label class="app-form__label">用户名</label>
    <div class="app-form__control">
      <input class="app-form__input" type="text" placeholder="请输入用户名" />
      <span class="app-form__error">用户名不能为空</span>
    </div>
  </div>

  <div class="app-form__item app-form__item--required">
    <label class="app-form__label">密码</label>
    <div class="app-form__control">
      <div class="app-form__input-group">
        <input class="app-form__input" type="password" />
        <button class="app-form__toggle-password">显示</button>
      </div>
      <span class="app-form__hint">密码长度 6-20 位</span>
    </div>
  </div>

  <div class="app-form__item">
    <label class="app-form__label">性别</label>
    <div class="app-form__control">
      <label class="app-radio">
        <input class="app-radio__input" type="radio" name="gender" />
        <span class="app-radio__label">男</span>
      </label>
      <label class="app-radio">
        <input class="app-radio__input" type="radio" name="gender" />
        <span class="app-radio__label">女</span>
      </label>
    </div>
  </div>

  <div class="app-form__item">
    <div class="app-form__control">
      <button class="app-button app-button--primary">提交</button>
      <button class="app-button app-button--default">重置</button>
    </div>
  </div>
</div>
```

```scss
@include b(form) {
  @include e(item) {
    display: flex;
    margin-bottom: 20px;
    @include m(required) {
      .app-form__label::before {
        content: '*';
        color: red;
        margin-right: 4px;
      }
    }
  }
  @include e(label) {
    width: 100px;
    text-align: right;
    padding-right: 12px;
    line-height: 32px;
  }
  @include e(control) {
    flex: 1;
    max-width: 400px;
  }
  @include e(input) {
    width: 100%;
    height: 32px;
    padding: 0 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }
  @include e(input-group) {
    display: flex;
    align-items: center;
  }
  @include e(toggle-password) {
    margin-left: 8px;
    cursor: pointer;
  }
  @include e(error) {
    display: block;
    color: #f5222d;
    font-size: 12px;
    margin-top: 4px;
  }
  @include e(hint) {
    display: block;
    color: #999;
    font-size: 12px;
    margin-top: 4px;
  }
}
```

### 5.5 复杂嵌套组件（下拉选择器）

```html
<!-- 下拉选择器 —— 深层嵌套 + 弹出层 -->
<div class="app-select">
  <!-- 触发器 -->
  <div class="app-select__trigger">
    <input class="app-select__input" readonly placeholder="请选择" />
    <span class="app-select__arrow app-select__arrow--expanded"></span>
  </div>

  <!-- 下拉面板（独立 Block） -->
  <div class="app-select-dropdown">
    <div class="app-select-dropdown__search">
      <input class="app-select-dropdown__search-input" placeholder="搜索" />
    </div>
    <ul class="app-select-dropdown__list">
      <li class="app-select-dropdown__item app-select-dropdown__item--selected">
        <span class="app-select-dropdown__label">选项一</span>
        <span class="app-select-dropdown__check"></span>
      </li>
      <li class="app-select-dropdown__item">
        <span class="app-select-dropdown__label">选项二</span>
      </li>
      <li class="app-select-dropdown__item app-select-dropdown__item--disabled">
        <span class="app-select-dropdown__label">选项三</span>
      </li>
    </ul>
    <div class="app-select-dropdown__empty">
      <span class="app-select-dropdown__empty-text">无匹配选项</span>
    </div>
  </div>
</div>
```

**设计决策：** 下拉面板 `app-select-dropdown` 提升为独立 Block（而非 `app-select__dropdown`），因为：
- 下拉面板在 DOM 中通常挂载到 `body` 下（避免 overflow 裁剪）
- 面板内部结构复杂（搜索框、列表、空状态），有 5+ 个子元素
- 面板可能被其他组件复用（如级联选择器、日期选择器）

### 5.6 页面级布局示例

```html
<!-- 管理后台页面布局 -->
<div class="app-layout">
  <!-- 侧边栏 -->
  <aside class="app-sidebar">
    <div class="app-sidebar__logo">
      <img class="app-sidebar__logo-img" src="logo.png" />
    </div>
    <nav class="app-menu">
      <div class="app-menu__item app-menu__item--active">
        <span class="app-menu__icon"></span>
        <span class="app-menu__label">工作台</span>
      </div>
      <div class="app-menu__group">
        <div class="app-menu__group-title">数据管理</div>
        <div class="app-menu__item">
          <span class="app-menu__label">用户列表</span>
        </div>
        <div class="app-menu__item">
          <span class="app-menu__label">订单列表</span>
        </div>
      </div>
    </nav>
  </aside>

  <!-- 主内容区 -->
  <main class="app-main">
    <div class="app-main__header">
      <div class="app-breadcrumb">
        <span class="app-breadcrumb__item">首页</span>
        <span class="app-breadcrumb__separator">/</span>
        <span class="app-breadcrumb__item app-breadcrumb__item--current">用户列表</span>
      </div>
    </div>
    <div class="app-main__content">
      <!-- 搜索表单（独立 Block） -->
      <div class="app-search-form">
        <div class="app-search-form__item">
          <input class="app-search-form__input" placeholder="用户名" />
        </div>
        <div class="app-search-form__actions">
          <button class="app-button app-button--primary">搜索</button>
          <button class="app-button app-button--default">重置</button>
        </div>
      </div>

      <!-- 数据表格 -->
      <div class="app-table">
        <!-- ... -->
      </div>
    </div>
  </main>
</div>
```

---

## 六、命名规则使用规范与注意事项

### 6.1 命名格式规范

| 规则 | 格式 | 示例 |
|------|------|------|
| 单词分隔 | 小写 + 连字符 `-` | `search-form`、`user-card` |
| Block 与 Element | `__` 双下划线 | `card__title`、`menu__item` |
| 修饰符 | `--` 双连字符 | `button--primary`、`card--large` |
| 状态前缀 | `is-` | `is-disabled`、`is-loading` |
| 命名空间 | `{prefix}-` | `app-button`、`app-modal` |

**禁止的命名方式：**

```
❌ 驼峰命名：    .userCard、.searchForm
❌ 下划线分隔：  .user_card、.search_form
❌ 单下划线修饰：.button_primary
❌ 双连字符连接词：.user--card（应理解为 Block user 的 --card 修饰符）
❌ 深层嵌套：    .card__body__list__item
❌ 无意义词：    .box、.wrap、.inner、.wrapper
```

### 6.2 SCSS Mixin 实现规范

```scss
// ===== 变量定义 =====
$namespace: 'app' !default;
$element-separator: '__' !default;
$modifier-separator: '--' !default;
$state-prefix: 'is-' !default;

// ===== Block Mixin =====
@mixin b($block) {
  $block-name: #{$namespace}-#{$block};
  .#{$block-name} {
    @content;
  }
}

// ===== Element Mixin =====
@mixin e($element) {
  $selector: &;
  @at-root {
    #{$selector + $element-separator + $element} {
      @content;
    }
  }
}

// ===== Modifier Mixin =====
@mixin m($modifier) {
  $selector: &;
  @at-root {
    #{$selector + $modifier-separator + $modifier} {
      @content;
    }
  }
}

// ===== 状态 Mixin =====
@mixin when($state) {
  @at-root {
    &.#{$state-prefix + $state} {
      @content;
    }
  }
}
```

**使用示例：**

```scss
@include b(button) {
  padding: 8px 16px;
  cursor: pointer;

  @include e(icon) {
    margin-right: 8px;
  }

  @include e(text) {
    font-size: 14px;
  }

  @include m(primary) {
    background: #1890ff;
    color: #fff;
  }

  @include m(disabled) {
    opacity: 0.5;
    cursor: not-allowed;
  }

  @include when(loading) {
    pointer-events: none;
  }
}
```

**编译输出：**

```css
.app-button { padding: 8px 16px; cursor: pointer; }
.app-button__icon { margin-right: 8px; }
.app-button__text { font-size: 14px; }
.app-button--primary { background: #1890ff; color: #fff; }
.app-button--disabled { opacity: 0.5; cursor: not-allowed; }
.app-button.is-loading { pointer-events: none; }
```

### 6.3 Block 划分原则

**六问法判断是否应成为独立 Block：**

```
1. 这个元素是否在多个不同的父组件中使用？
   → 是 → 独立 Block

2. 这个元素是否有独立的业务含义？
   → 是 → 独立 Block

3. 这个元素内部是否有 3 个以上子元素？
   → 是 → 考虑独立 Block

4. 这个元素是否可能被移到 DOM 的其他位置（如 portal 到 body）？
   → 是 → 独立 Block

5. 其他开发者看到这个元素名，能否独立理解其含义？
   → 否 → 独立 Block

6. 这个元素是否只服务于当前 Block 的布局目的？
   → 是 → 作为 Element
```

### 6.4 常见陷阱与解决方案

**陷阱一：位置命名**

```html
<!-- ❌ 用位置命名 -->
<div class="sidebar__btn"></div>
<div class="page-header__search"></div>

<!-- ✅ 用语义命名 -->
<button class="app-button app-button--icon"></button>
<div class="app-search-bar"></div>
```

**陷阱二：视觉描述命名**

```html
<!-- ❌ 用视觉描述 -->
<span class="app-text--red">错误信息</span>
<div class="app-card--big">大卡片</div>

<!-- ✅ 用语义命名 -->
<span class="app-text--danger">错误信息</span>
<div class="app-card--large">大卡片</div>
```

**陷阱三：过度拆分 Element**

```html
<!-- ❌ 不必拆分出来的 Element -->
<div class="app-card">
  <div class="app-card__padding-wrapper">
    <div class="app-card__content-container">
      <p class="app-card__text">内容</p>
    </div>
  </div>
</div>

<!-- ✅ 去掉无意义的容器 Element -->
<div class="app-card">
  <p class="app-card__text">内容</p>
</div>
```

**陷阱四：在 SCSS 中制造后代选择器**

```scss
// ❌ 危险写法：生成 .app-card__header .app-card__title
@include b(card) {
  @include e(header) {
    @include e(title) {  // 嵌套的 e() 会继承 selector 上下文
      font-size: 18px;
    }
  }
}

// ✅ 安全写法：所有 e() 都在 b() 层级
@include b(card) {
  @include e(header) { padding: 16px; }
  @include e(title)  { font-size: 18px; }
}
```

### 6.5 第三方组件覆盖规范

覆盖 Element Plus 等第三方组件样式时，使用 **Wrapper Block 语义隔离**：

```html
<!-- ✅ 正确：外层包裹语义 Block -->
<div class="app-user-form">
  <el-input v-model="username" placeholder="用户名" />
  <el-select v-model="role">
    <el-option label="管理员" value="admin" />
  </el-select>
</div>
```

```scss
// ✅ 通过 Wrapper Block 限定作用域
.app-user-form {
  .el-input {
    width: 300px;
  }
  .el-select {
    margin-left: 16px;
  }
}
```

**禁止做法：**

```scss
// ❌ 直接修改第三方组件全局样式
.el-input { width: 300px; }

// ❌ 强行修改第三方组件的 BEM 类名
// ❌ 使用 !important 覆盖
// ❌ 使用 ID 选择器提高优先级
```

---

## 附录：命名速查表

### Block 命名速查

| 场景 | 命名 |
|------|------|
| 按钮 | `app-button` |
| 输入框 | `app-input` |
| 选择器 | `app-select` |
| 卡片 | `app-card` |
| 表格 | `app-table` |
| 弹窗 | `app-modal` / `app-dialog` |
| 表单 | `app-form` |
| 菜单 | `app-menu` |
| 标签页 | `app-tabs` |
| 面包屑 | `app-breadcrumb` |
| 分页 | `app-pagination` |
| 下拉面板 | `app-dropdown` / `app-select-dropdown` |

### Modifier 命名速查

| 类型 | 命名 |
|------|------|
| 尺寸 | `--large`、`--default`、`--small` |
| 主题色 | `--primary`、`--success`、`--warning`、`--danger`、`--info` |
| 布局 | `--horizontal`、`--vertical` |
| 形状 | `--round`、`--circle` |
| 状态 | `--disabled`、`--loading`、`--active`、`--selected` |

### 状态类命名速查

| 状态 | 命名 |
|------|------|
| 禁用 | `is-disabled` |
| 加载 | `is-loading` |
| 激活 | `is-active` |
| 展开 | `is-expanded` |
| 选中 | `is-selected` |
| 可见 | `is-visible` |
| 错误 | `is-error` |
| 只读 | `is-readonly` |

### 规则优先级总结

```
1. 命名空间前缀：app-{block}
2. 扁平化 Element：block__element（仅一级）
3. 语义化 Modifier：block--modifier
4. 动态状态：is-{state}
5. 子 Block 提升：复杂度 > 3 或可复用 → 独立 Block
6. Wrapper 隔离：第三方组件覆盖使用 app-{wrapper} .el-{component}
```

---

> **参考资源：**
> - [Element Plus 官方文档](https://element-plus.org/zh-CN/component/overview)
> - [Element Plus useNamespace 源码](https://github.com/element-plus/element-plus)
> - [BEM 官方文档](https://en.bem.info/methodology/)
> - [Sass @at-root 文档](https://sass-lang.com/documentation/at-rules/at-root)