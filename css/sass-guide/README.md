# Sass 使用指南

本目录包含了完整的 Sass 使用指南，包括文档、示例代码和实际应用。

## 文件结构

```
sass-guide/
├── sass-usage-guide.md          # Sass 使用指南（Markdown 版本）
├── sass-usage-guide.html        # Sass 使用指南（HTML 版本）
├── example.scss                 # Sass 示例源代码
├── example.css                  # 编译后的 CSS 文件
├── example.min.css              # 压缩后的 CSS 文件
├── package.json                 # 项目配置和脚本
└── README.md                    # 本文件
```

## 内容概述

### 1. Sass 使用指南（Markdown）
- **文件**: `sass-usage-guide.md`
- **内容**: 完整的 Sass 学习指南，包含：
  - Sass 简介和两种语法对比
  - 核心特性：变量、嵌套、混合、继承、函数
  - 控制指令：@if、@for、@each、@while
  - 模块化：@import、@use、@forward
  - 安装和使用方法
  - 最佳实践和文件组织
  - 实际应用示例

### 2. Sass 使用指南（HTML）
- **文件**: `sass-usage-guide.html`
- **内容**: 交互式的 HTML 版本指南，包含：
  - 美观的响应式设计
  - 代码语法高亮
  - 实际效果演示
  - 交互式示例
  - 可直接在浏览器中打开查看

### 3. Sass 示例代码
- **文件**: `example.scss`
- **内容**: 完整的 Sass 示例，展示：
  - 变量定义和管理
  - 混合（Mixins）的创建和使用
  - 函数定义和计算
  - 组件化开发（按钮、卡片、表单等）
  - 响应式设计实现
  - 工具类和实用功能

### 4. 编译后的 CSS
- **文件**: `example.css`
- **内容**: 展示 Sass 编译后的实际 CSS 代码
- **特点**: 可以看到 Sass 高级功能如何转换为标准 CSS

### 5. 项目配置
- **文件**: `package.json`
- **内容**: 包含 Sass 编译脚本和依赖配置

## 快速开始

### 安装 Sass

```bash
# 全局安装
npm install -g sass

# 或本地安装（推荐）
npm install
```

### 使用示例

1. **编译单个文件**:
   ```bash
   npm run sass:compile
   ```

2. **监听文件变化**:
   ```bash
   npm run sass:watch
   ```

3. **构建压缩版本**:
   ```bash
   npm run sass:build
   ```

4. **启动开发服务器**:
   ```bash
   npm run serve
   ```

## Sass 核心特性示例

### 变量
```scss
$primary-color: #3498db;
$spacing-unit: 8px;

.header {
  background: $primary-color;
  padding: $spacing-unit * 2;
}
```

### 嵌套
```scss
.nav {
  ul {
    margin: 0;
    padding: 0;
    
    li {
      display: inline-block;
      
      a {
        color: #333;
        
        &:hover {
          color: #3498db;
        }
      }
    }
  }
}
```

### 混合（Mixins）
```scss
@mixin flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

@mixin respond-to($breakpoint) {
  @media (min-width: $breakpoint) {
    @content;
  }
}

.container {
  @include flex-center;
  
  @include respond-to(768px) {
    width: 750px;
  }
}
```

### 函数
```scss
@function rem($px) {
  @return ($px / 16px) * 1rem;
}

@function spacing($multiplier) {
  @return $multiplier * 8px;
}

body {
  font-size: rem(16px);
  margin: spacing(2);
}
```

## 最佳实践

### 1. 文件组织
```
scss/
├── abstracts/     # 抽象层（变量、函数、混合）
├── base/         # 基础样式（重置、排版）
├── components/   # 组件样式
├── layout/       # 布局样式
├── pages/        # 页面特定样式
├── themes/       # 主题样式
└── main.scss     # 主入口文件
```

### 2. 命名规范
- 使用 BEM 命名法：`.block__element--modifier`
- 变量使用连字符：`$primary-color`
- 混合使用动词：`@mixin center-element`

### 3. 性能优化
- 避免过度嵌套（不超过 4 层）
- 合理使用继承和混合
- 压缩生产环境代码

## 学习路径

1. **初学者**: 从 `sass-usage-guide.html` 开始，了解基本概念
2. **实践者**: 查看 `example.scss` 学习实际应用
3. **进阶者**: 研究编译后的 `example.css` 理解转换过程

## 资源链接

- [Sass 官方文档](https://sass-lang.com/documentation)
- [Sass Guidelines（中文）](https://sass-guidelin.es/zh/)
- [Sass Playground](https://www.sassmeister.com/)

## 许可证

MIT License - 自由使用和修改