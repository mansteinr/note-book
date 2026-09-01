# Monorepo 简介及代码演示

## 一、什么是 Monorepo？

**Monorepo（单一仓库）**是一种项目管理方式：

> 一个 Git 仓库中，同时管理多个项目、应用和公共代码包。

例如：

```text
my-project/
├── apps/
│   ├── web/          # Web 主应用
│   └── admin/        # 管理后台
│
├── packages/
│   ├── ui/           # 公共组件
│   ├── utils/        # 公共工具
│   └── request/      # 公共请求库
│
├── package.json
└── pnpm-workspace.yaml
```

可以理解成：

```text
                    Monorepo
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
        apps        packages      configs
          │            │
      ┌───┴───┐    ┌───┼────┐
      ▼       ▼    ▼   ▼    ▼
     web    admin  ui utils request
```

---

# 二、Monorepo 和 Multirepo 的区别

## Multirepo

传统方式是一个项目一个仓库：

```text
Git仓库
├── web
│
├── admin
│
├── ui
│
└── utils
```

修改公共 UI：

```text
ui
 ↓
发布npm
 ↓
web升级版本
 ↓
admin升级版本
```

---

## Monorepo

所有项目放在一个仓库：

```text
Git仓库
│
├── apps
│   ├── web
│   └── admin
│
└── packages
    ├── ui
    └── utils
```

可以直接：

```text
web
 ↓
packages/ui
```

不需要每次修改都先发布 npm。

---

# 三、Monorepo 的优点

## 1. 代码复用方便

多个项目可以直接使用公共包：

```text
web ───────┐
           │
admin ─────┼──→ packages/utils
           │
mobile ────┘
```

---

## 2. 统一管理依赖

例如统一 Vue 版本：

```json
{
  "dependencies": {
    "vue": "^3.5.0"
  }
}
```

可以降低多个项目依赖版本不一致的问题。

---

## 3. 修改公共代码方便

例如：

```text
packages/ui
```

修改一个 Button：

```text
Button.vue
```

使用它的：

```text
web
admin
```

可以直接进行联调。

---

## 4. 统一代码规范

可以统一：

```text
ESLint
Prettier
TypeScript
Commitlint
Git Hooks
```

目录：

```text
packages/
├── eslint-config/
├── tsconfig/
└── prettier-config/
```

---

# 四、Monorepo 的缺点

Monorepo 也不是没有问题。

### 1. 项目规模变大

所有代码都在一个仓库：

```text
100个应用
+
200个package
```

Git 仓库可能非常庞大。

---

### 2. 构建复杂

修改一个公共包：

```text
packages/utils
```

可能影响：

```text
web
admin
mobile
```

需要合理设计构建依赖关系。

---

### 3. CI/CD 更复杂

需要判断：

```text
哪个项目发生变化？
哪个项目需要重新构建？
哪些项目需要重新部署？
```

因此大型项目通常会结合：

```text
Monorepo
+
Turborepo / Nx
+
CI/CD
```

---

# 五、使用 pnpm 创建 Monorepo

这里使用：

```text
pnpm + workspace
```

这是目前前端非常常见的一种方案。

首先创建：

```text
monorepo-demo/
```

---

# 六、项目目录

最终目录：

```text
monorepo-demo/
│
├── apps/
│   ├── web/
│   └── admin/
│
├── packages/
│   ├── utils/
│   └── ui/
│
├── package.json
│
└── pnpm-workspace.yaml
```

---

# 七、根目录 package.json

```json
{
  "name": "monorepo-demo",
  "private": true,
  "scripts": {
    "dev:web": "pnpm --filter web dev",
    "dev:admin": "pnpm --filter admin dev"
  }
}
```

这里：

```json
{
  "private": true
}
```

表示根项目不是一个需要发布到 npm 的包。

---

# 八、pnpm-workspace.yaml

根目录创建：

```text
pnpm-workspace.yaml
```

内容：

```yaml
packages:
  - "apps/*"
  - "packages/*"
```

意思是：

```text
apps/*
    ↓
所有应用

packages/*
    ↓
所有公共包
```

例如：

```text
apps/web
apps/admin

packages/ui
packages/utils
```

都会被 pnpm 识别为 Workspace 项目。

---

# 九、创建 utils 公共包

目录：

```text
packages/
└── utils/
    ├── package.json
    └── src/
        └── index.ts
```

### package.json

```json
{
  "name": "@demo/utils",
  "version": "1.0.0",
  "main": "src/index.ts"
}
```

---

## utils/index.ts

```typescript
export function formatName(name: string) {
  return `Hello ${name}`;
}

export function add(a: number, b: number) {
  return a + b;
}
```

---

# 十、在 Web 项目中使用 utils

例如：

```text
apps/web/
├── package.json
└── src/
    └── main.ts
```

`apps/web/package.json`：

```json
{
  "name": "web",
  "dependencies": {
    "@demo/utils": "workspace:*"
  }
}
```

重点：

```text
workspace:*
```

表示：

> 当前项目优先使用 Monorepo Workspace 中的本地包。

---

# 十一、Web 项目调用 utils

```typescript
import { formatName, add } from '@demo/utils';

console.log(formatName('Tom'));

console.log(add(10, 20));
```

输出：

```text
Hello Tom
30
```

这里没有：

```bash
npm publish
```

也没有：

```bash
npm install @demo/utils
```

直接使用 Workspace 中的本地包。

---

# 十二、创建 Vue3 公共组件库

目录：

```text
packages/
└── ui/
    ├── package.json
    └── src/
        ├── Button.vue
        └── index.ts
```

---

## Button.vue

```vue
<template>
  <button class="demo-button">
    <slot />
  </button>
</template>

<style scoped>
.demo-button {
  padding: 8px 16px;
  border-radius: 4px;
  border: 1px solid #ddd;
  cursor: pointer;
}
</style>
```

---

# 十三、ui/index.ts

```typescript
import Button from './Button.vue';

export {
  Button
};
```

---

# 十四、ui/package.json

```json
{
  "name": "@demo/ui",
  "version": "1.0.0",
  "main": "src/index.ts",
  "peerDependencies": {
    "vue": "^3.0.0"
  }
}
```

这里使用：

```json
"peerDependencies"
```

表示：

> UI 组件库依赖宿主项目提供 Vue，而不是自己重复安装一份 Vue。

---

# 十五、Web 项目依赖 UI

`apps/web/package.json`：

```json
{
  "name": "web",
  "dependencies": {
    "@demo/ui": "workspace:*",
    "@demo/utils": "workspace:*"
  }
}
```

然后：

```bash
pnpm install
```

---

# 十六、Vue3 中使用公共组件

```vue
<script setup lang="ts">
import { Button } from '@demo/ui';
</script>

<template>
  <div>
    <h1>Web App</h1>

    <Button>
      点击按钮
    </Button>
  </div>
</template>
```

最终关系：

```text
apps/web
   │
   ├── @demo/ui
   │
   └── @demo/utils
```

---

# 十七、完整项目结构

最终：

```text
monorepo-demo/
│
├── apps/
│   │
│   ├── web/
│   │   ├── src/
│   │   │   └── App.vue
│   │   └── package.json
│   │
│   └── admin/
│       ├── src/
│       └── package.json
│
├── packages/
│   │
│   ├── ui/
│   │   ├── src/
│   │   │   ├── Button.vue
│   │   │   └── index.ts
│   │   └── package.json
│   │
│   └── utils/
│       ├── src/
│       │   └── index.ts
│       └── package.json
│
├── package.json
│
└── pnpm-workspace.yaml
```

---

# 十八、常用 pnpm 命令

## 安装所有依赖

```bash
pnpm install
```

---

## 启动 web

```bash
pnpm --filter web dev
```

---

## 启动 admin

```bash
pnpm --filter admin dev
```

---

## 给 web 安装依赖

```bash
pnpm --filter web add axios
```

---

## 给公共 utils 添加依赖

```bash
pnpm --filter @demo/utils add lodash
```

---

## 构建所有项目

```bash
pnpm -r build
```

其中：

```text
-r
```

表示递归执行 Workspace 中的项目。

---

# 十九、Monorepo + 微前端

Monorepo 和微前端不是一个概念。

可以组合使用：

```text
                    Monorepo
                       │
           ┌───────────┼───────────┐
           │           │           │
           ▼           ▼           ▼
        主应用       子应用A      子应用B
           │           │           │
           │         Vue3        React
           │
           └──────────┬────────────┘
                      │
                Wujie / qiankun
```

两者解决的问题不同：

```text
Monorepo
↓
代码组织和工程管理

Wujie
↓
运行时微前端
```

---

# 二十、Monorepo + Wujie 的实际应用

例如一个企业级系统：

```text
monorepo/
│
├── apps/
│   ├── main/
│   │
│   ├── user/
│   │
│   ├── order/
│   │
│   └── monitor/
│
└── packages/
    ├── ui/
    ├── utils/
    ├── request/
    ├── auth/
    └── websocket/
```

其中：

```text
main
 ↓
Wujie
 ↓
user
order
monitor
```

公共代码：

```text
ui
utils
request
auth
websocket
```

可以被多个应用复用。

最终形成：

```text
                Monorepo
                   │
       ┌───────────┴───────────┐
       │                       │
    apps                    packages
       │                       │
 ┌─────┼─────┐       ┌─────────┼─────────┐
 ▼     ▼     ▼       ▼         ▼         ▼
main  user  order    ui       utils    request
 │
 └──────── Wujie ────────┐
                         │
                    微前端运行
```

---

# 二十一、Monorepo 面试怎么回答

面试官：

> 什么是 Monorepo？

可以回答：

> Monorepo 是一种代码仓库管理方式，把多个应用和公共 package 放在同一个 Git 仓库中统一管理。
>
> 比如我们可以把 Vue 主应用、管理后台、公共 UI 组件、utils、request SDK 放在同一个仓库。
>
> 我们项目中可以使用 pnpm workspace 管理依赖，通过 workspace 协议让应用直接依赖本地 package。
>
> 相比 Multirepo，Monorepo 最大的优势是公共代码复用和版本管理更加方便，同时可以统一 ESLint、TypeScript、构建和 CI/CD 配置。
>
> 但是随着项目规模扩大，构建和 CI/CD 的复杂度也会增加，因此大型项目通常会结合 Turborepo 或 Nx 做任务编排、缓存和增量构建。

---

# 二十二、面试重点

如果面试官问 Monorepo，建议重点掌握：

```text
                 Monorepo
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
     Workspace    依赖管理    构建系统
        │           │           │
       pnpm       workspace    Turbo/Nx
        │
        ▼
   packages复用
        │
        ▼
    CI/CD增量构建
```

重点记住：

1. **Monorepo 是一种工程管理模式**
2. **pnpm workspace 可以管理 Monorepo**
3. **workspace:* 可以引用本地 package**
4. **packages 可以存放公共 UI、utils、SDK**
5. **Monorepo 不等于微前端**
6. **Monorepo 解决代码组织问题，Wujie 解决运行时微前端问题**
7. **大型项目可以使用 Turborepo / Nx 优化构建和 CI/CD**

---

# 二十三、一句话总结

> **Monorepo = 一个 Git 仓库管理多个 App 和 Package，通过 Workspace 管理依赖和代码复用；它主要解决大型前端项目的工程组织问题，而不是运行时隔离问题。**