# Monorepo 详细介绍与实践指南

> 本文档系统介绍 Monorepo 架构的核心概念、优势与适用场景、常见实现方案、项目结构设计、依赖管理策略、构建部署流程以及实际开发中的最佳实践，为团队提供系统性的认知和实施指导。

---

## 目录

- [一、Monorepo 核心概念](#一monorepo-核心概念)
- [二、Monorepo 与 Polyrepo 对比](#二monorepo-与-polyrepo-对比)
- [三、Monorepo 优势与适用场景](#三monorepo-优势与适用场景)
- [四、常见 Monorepo 实现方案](#四常见-monorepo-实现方案)
- [五、项目结构设计原则](#五项目结构设计原则)
- [六、依赖管理策略](#六依赖管理策略)
- [七、构建与部署流程](#七构建与部署流程)
- [八、pnpm + Turborepo 实战配置](#八pnpm--turborepo-实战配置)
- [九、最佳实践与注意事项](#九最佳实践与注意事项)
- [十、常见问题 FAQ](#十常见问题-faq)

---

## 一、Monorepo 核心概念

### 1.1 什么是 Monorepo

**Monorepo**（Monolithic Repository，单体仓库）是一种代码管理架构，指将多个独立的项目/包存储在同一个版本控制仓库中。

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Monorepo 架构示意                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  my-monorepo/                                                      │
│  ├── .git/                    ← 单一 Git 仓库                      │
│  ├── packages/                 ← 多个子项目/包                      │
│  │   ├── ui/                 ← UI 组件库                           │
│  │   ├── utils/              ← 工具函数库                          │
│  │   ├── api-client/         ← API 客户端                         │
│  │   ├── admin-web/          ← 管理后台应用                        │
│  │   ├── user-web/           ← 用户端应用                          │
│  │   └── mobile-app/         ← 移动端应用                          │
│  ├── apps/                     ← 可部署应用                         │
│  │   └── docs/               ← 文档站点                            │
│  ├── package.json             ← 根级依赖和脚本                      │
│  ├── pnpm-workspace.yaml      ← 工作区配置                          │
│  └── turbo.json               ← 构建工具配置                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Monorepo 的核心特征

| 特征 | 说明 |
|------|------|
| **单一版本控制** | 所有子项目共享一个 Git 仓库 |
| **独立发布** | 每个子项目可以独立版本发布 |
| **代码共享** | 子项目之间可以互相引用 |
| **统一依赖** | 公共依赖提升到根目录管理 |
| **独立运行** | 每个子项目可以独立构建、测试、部署 |

### 1.3 Monorepo 不是什么

- **不是 Monolith（单体应用）**：Monorepo 是代码组织方式，不是架构模式；Monolith 是将所有功能打包为单一部署单元
- **不是 Microfrontend（微前端）的对立面**：微前端可以用 Monorepo 管理，也可以用 Polyrepo
- **不是必须用特定工具**：Monorepo 可以只用 Git 实现，工具只是锦上添花

---

## 二、Monorepo 与 Polyrepo 对比

### 2.1 Polyrepo 架构

**Polyrepo**（多仓库）：每个项目/包一个独立的 Git 仓库。

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Polyrepo 架构示意                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  repo-ui/                    repo-utils/                            │
│  ├── src/                    ├── src/                               │
│  ├── package.json           ├── package.json                        │
│  └── .git/                  └── .git/                               │
│                                                                     │
│  repo-admin-web/             repo-user-web/                         │
│  ├── src/                    ├── src/                               │
│  ├── package.json           ├── package.json                        │
│  └── .git/                  └── .git/                               │
│                                                                     │
│  每个仓库独立开发、测试、版本管理、CI/CD                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 核心对比表

| 对比维度 | Monorepo | Polyrepo |
|---------|----------|----------|
| **版本控制** | 单一 Git 仓库 | 多个独立 Git 仓库 |
| **代码共享** | 直接引用，即时生效 | 需要发布 npm 包或 Git 子模块 |
| **依赖管理** | 统一管理，版本一致 | 各项目独立，版本可能冲突 |
| **跨包修改** | 一次提交，原子化修改 | 需要多个仓库协调，容易出错 |
| **原子提交** | 支持（一次 commit 改多个包） | 不支持 |
| **代码可见性** | 所有代码可见 | 只能看到当前仓库 |
| **仓库体积** | 可能很大，clone 慢 | 每个仓库较小 |
| **权限控制** | 较粗粒度，不易分仓库权限 | 细粒度，每个仓库独立权限 |
| **CI/CD** | 需要工具支持增量构建 | 各自独立流水线 |
| **学习成本** | 统一规范，学习简单 | 每个仓库规范可能不同 |
| **发布流程** | 复杂，需要处理依赖关系 | 简单，各自独立发布 |
| **构建性能** | 需要工具优化，否则可能很慢 | 各自构建，互不影响 |
| **团队协作** | 适合紧密协作的团队 | 适合独立团队 |

### 2.3 选择决策树

```
┌─────────────────────────────────────────────────────────────────────┐
│                     选择 Monorepo 还是 Polyrepo？                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Q1: 团队是多团队还是单团队？                                        │
│  ├── 多团队 + 代码隔离要求高 → Polyrepo                             │
│  └── 单/少团队 → 继续判断 Q2                                        │
│                                                                     │
│  Q2: 项目之间代码共享程度？                                          │
│  ├── 高度共享（共享 UI、utils、types）→ Monorepo                    │
│  └── 低共享 → 继续判断 Q3                                            │
│                                                                     │
│  Q3: 跨项目协调修改频率？                                            │
│  ├── 经常需要同时改多个项目 → Monorepo                              │
│  └── 很少 → 两者均可                                                │
│                                                                     │
│  Q4: CI/CD 和部署是否独立？                                          │
│  ├── 完全独立（不关心其他项目）→ Polyrepo                            │
│  └── 有依赖关系 → Monorepo                                          │
│                                                                     │
│  Q5: 是否有严格的权限隔离需求？                                      │
│  ├── 有（不同团队不能互看代码）→ Polyrepo                            │
│  └── 无 → 倾向 Monorepo                                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 三、Monorepo 优势与适用场景

### 3.1 Monorepo 的优势

#### ✅ 优势一：代码共享与复用

```javascript
// ❌ Polyrepo：需要先发布 ui 包到 npm，再在 admin-web 中安装更新
// admin-web/package.json
{
  "dependencies": {
    "@company/ui": "^1.2.3"  // 可能滞后最新修改
  }
}

// ✅ Monorepo：直接引用本地代码，即时生效
// admin-web/package.json
{
  "dependencies": {
    "@company/ui": "workspace:*"  // 引用 workspace 内的包，修改立即生效
  }
}
```

**价值**：
- 无需 npm 发布流程即可共享代码
- 修改共享库后，所有依赖方立即看到效果
- 避免"一个小改动需要跨多个仓库发版"

#### ✅ 优势二：原子化提交

```bash
# ❌ Polyrepo：修改 UI 组件并在 Admin 中使用需要多次提交
# repo-ui
git commit -m "feat: Button 新增 size 属性"
git tag v1.1.0
npm publish

# repo-admin-web（等 ui 包发布后）
npm update @company/ui
git commit -m "chore: 更新 ui 包，使用 Button 新属性"

# ✅ Monorepo：一次提交完成所有修改
git commit -m "feat: Button 新增 size 属性并在 Admin 页面应用"
# 包含 ui 和 admin-web 两个 package 的修改
```

#### ✅ 优势三：统一依赖版本

```
Monorepo 依赖管理（以 pnpm 为例）：

my-monorepo/
├── node_modules/          ← 公共依赖提升到根目录（去重）
│   └── vue@3.3.4         ← 所有子项目共享同一个 Vue 实例
├── packages/
│   ├── admin-web/
│   │   └── package.json  ← 声明依赖 vue@^3.3.4
│   ├── user-web/
│   │   └── package.json  ← 声明依赖 vue@^3.3.4
│   └── ui/
│       └── package.json  ← 声明依赖 vue@^3.3.4
└── package.json

结果：
- 只安装一个 vue 副本，节省磁盘空间
- 不会出现多个 Vue 实例导致的错误
- 升级 vue 只需修改根 package.json 一处
```

#### ✅ 优势四：跨项目重构更安全

```javascript
// 重构 utils 包的函数签名
// packages/utils/src/format.ts

// ❌ Polyrepo：很难知道哪些项目用到了这个函数
export function formatDate(date, format) { ... }

// ✅ Monorepo：全仓库搜索引用，IDE 一键重构，编译器检查所有调用处
export function formatDate(date: Date, format: string, options?: FormatOptions) { ... }
// 所有调用处如果不传 options 就会报错
```

#### ✅ 优势五：统一的开发规范和工具链

```
Monorepo 统一规范：

my-monorepo/
├── .eslintrc.cjs       ← 统一 ESLint 配置
├── .prettierrc         ← 统一 Prettier 配置
├── tsconfig.base.json  ← 统一 TypeScript 基础配置
├── jest.config.ts      ← 统一 Jest 配置
└── .husky/             ← 统一 Git Hooks
    └── pre-commit

效果：
- 所有子项目自动继承统一规范
- 新项目不需要反复配置工具链
- 代码风格高度一致
```

### 3.2 Monorepo 的挑战

| 挑战 | 说明 | 解决方案 |
|------|------|---------|
| **仓库体积过大** | Git clone/pull 变慢 | 使用 sparse checkout、Git LFS、shallow clone |
| **构建时间长** | 改动一个包可能触发很多构建 | 使用 Turborepo/Nx 增量构建和远程缓存 |
| **版本发布复杂** | 多包版本依赖处理 | 使用 Changesets、Lerna、pnpm publish |
| **权限管理粗** | 难以对个别包设权限 | 使用 CODEOWNERS 文件、PR 审核 |
| **CI 流水线复杂** | 需要确定影响范围 | 使用工具的 affected 检测能力 |
| **新人学习曲线** | 需要理解整个仓库结构 | 提供清晰的文档和目录说明 |

### 3.3 适用场景

#### ✅ 推荐使用 Monorepo 的场景

1. **大型前端组织**：多个团队共享组件库、工具库
   - 例：阿里、字节、腾讯等大厂的前端架构

2. **微前端/多端应用**：
   - Web（管理后台 + 用户端 + 文档站）
   - Mobile（React Native / UniApp）
   - 小程序

3. **组件库/SDK 生态系统**：
   - UI 组件库 + 多个 Demo + 文档站
   - SDK + 示例项目 + 测试

4. **全栈 TypeScript 项目**：
   - 后端（NestJS/Express）+ 前端（Vue/React）+ 共享 types
   ```
   project/
   ├── packages/
   │   ├── server/     ← NestJS 后端
   │   ├── client/     ← Vue 前端
   │   └── shared/     ← 共享 TypeScript 类型定义
   ```

5. **需要频繁跨项目协作的小型团队**：
   - 团队规模 5-20 人
   - 多个项目之间紧密关联

#### ❌ 不推荐使用 Monorepo 的场景

1. **完全独立的团队/项目**：项目之间没有任何联系
2. **严格的安全隔离要求**：不同团队之间代码不可见
3. **超大仓库（千万行代码+）**：Git 性能问题严重（可考虑 Monorepo + 稀疏检出）
4. **成熟的独立开源项目**：每个项目需要独立的社区和 issue 管理

---

## 四、常见 Monorepo 实现方案

### 4.1 方案对比总览

| 方案 | 类型 | 核心能力 | 包管理 | 构建缓存 | 适用场景 |
|------|------|---------|--------|---------|---------|
| **pnpm Workspace** | 包管理器 | 依赖管理、workspace | ✅ | ❌ | 基础 Monorepo，配合其他工具 |
| **Lerna** | 全功能 | 版本发布、依赖管理、构建 | ⚠️ | ⚠️ Lerna 6+ | 传统项目，需要版本管理 |
| **Nx** | 构建工具 | 智能构建、缓存、代码生成 | ✅ | ✅ 强 | 大型企业项目，需要智能分析 |
| **Turborepo** | 构建工具 | 增量构建、远程缓存 | ❌ 配合 pnpm | ✅ 强 | 追求高性能，与 Vite/Next 生态契合 |
| **Rush** | 全功能 | 全流程管理，企业级 | ✅ | ✅ | 超大型项目，微软出品 |
| **Yarn Workspace** | 包管理器 | 依赖管理 | ✅ | ❌ | 已用 Yarn 的项目 |
| **Bazel** | 构建工具 | 语言无关，极致性能 | ❌ | ✅ 最强 | 超大规模，Google 出品 |

### 4.2 pnpm Workspace（推荐组合的基础）

**定位**：依赖管理工具 + workspace 基础能力（不负责构建调度）

#### 优点
- 最快的包管理器（硬链接 + 内容寻址存储）
- 节省磁盘空间（依赖只存一份）
- 严格的依赖隔离（Phantom 依赖检测）
- 配置简单，社区广泛使用

#### 配置示例

```yaml
# pnpm-workspace.yaml
packages:
  # 所有 packages 下的子目录
  - 'packages/*'
  # 所有 apps 下的子目录
  - 'apps/*'
  # 排除目录
  - '!**/test-fixtures'
  - '!packages/*/test'
```

```json
// package.json（根目录）
{
  "name": "my-monorepo",
  "private": true,  // 根 package 必须设为 private，不发布
  "version": "0.0.0",
  "scripts": {
    "dev": "pnpm --filter admin-web dev",
    "build": "pnpm -r build",
    "test": "pnpm -r test"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "eslint": "^8.0.0",
    "prettier": "^2.8.0"
  }
}
```

**常用命令**：

```bash
# 安装所有依赖（根目录）
pnpm install

# 给所有包执行 build 命令（按依赖顺序）
pnpm -r build

# 并行执行（8 个并发）
pnpm -r --parallel --stream build

# 只对 admin-web 包执行命令
pnpm --filter admin-web dev
pnpm -F admin-web build  # 简写

# 对 admin-web 及其依赖包执行
pnpm -F admin-web... build

# 对被 admin-web 依赖的包执行（包括自己）
pnpm -F ...admin-web build

# 添加公共依赖到根目录
pnpm add -Dw typescript

# 给指定包添加依赖
pnpm -F @company/ui add element-plus

# 包之间互相引用（workspace 协议）
pnpm -F admin-web add @company/ui@workspace:*
```

### 4.3 Turborepo（构建加速）

**定位**：高性能构建系统（负责构建调度、缓存、增量构建）

#### 优点
- 任务调度（自动识别依赖关系，按序构建）
- 本地缓存 + 远程缓存（S3/云存储，跨机器共享）
- 增量构建（只构建有改动的包）
- 与 pnpm/npm/yarn 无缝配合
- 配置简单，零侵入

#### 配置示例

```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": [
    "tsconfig.base.json",
    ".env.*"
  ],
  "tasks": {
    "build": {
      "dependsOn": ["^build"],  // 依赖项的 build 必须先完成
      "outputs": ["dist/**", ".next/**"],  // 构建产物
      "inputs": ["src/**/*.ts", "src/**/*.vue"]  // 输入源文件
    },
    "dev": {
      "dependsOn": ["^build"],
      "cache": false,  // dev 不需要缓存
      "persistent": true  // 持久进程，不退出
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    },
    "lint": {
      "outputs": []
    },
    "clean": {
      "cache": false
    }
  }
}
```

```json
// 根 package.json 添加脚本
{
  "scripts": {
    "dev": "turbo dev",
    "build": "turbo build",
    "test": "turbo test",
    "lint": "turbo lint",
    "clean": "turbo clean"
  },
  "devDependencies": {
    "turbo": "^1.10.0"
  }
}
```

**常用命令**：

```bash
# 构建所有包（自动处理依赖顺序 + 缓存）
turbo build

# 只构建 admin-web 和其依赖
turbo build --filter=admin-web

# 启动多个服务的 dev（同时启动 admin-web 和 docs）
turbo dev --filter=admin-web --filter=docs --parallel

# 查看依赖关系图
turbo build --dry=json

# 配置远程缓存（需要登录 Turborepo 账号）
npx turbo login
npx turbo link
```

**远程缓存架构**：

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Turborepo 远程缓存                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  开发者 A → 本地构建 → 上传构建产物 → 远程缓存（Vercel/S3）          │
│                                                                ↓    │
│  开发者 B → 开始构建 → 查询缓存 → 命中远程缓存 → 秒级完成          │
│                                                                ↓    │
│  CI 流水线  → 查询缓存 → 命中 → 跳过构建，直接部署                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.4 Nx（企业级方案）

**定位**：全功能 Monorepo 框架（包含构建、代码生成、可视化、测试）

#### 优点
- 受影响项目检测（affected 分析）
- 高级依赖图可视化
- 代码生成（schematics）
- 企业级功能（自定义插件、分布式任务执行）
- 社区插件生态丰富（Vue、React、NestJS、Next.js 等）

#### 配置示例

```bash
# 创建 Nx Monorepo
npx create-nx-workspace@latest myorg

# 添加应用
nx g @nx/vue:app admin-web
nx g @nx/vue:app user-web

# 添加库
nx g @nx/vue:lib ui
nx g @nx/js:lib utils
```

```json
// nx.json
{
  "$schema": "./node_modules/nx/schemas/nx-schema.json",
  "tasksRunnerOptions": {
    "default": {
      "runner": "nx/tasks-runners/default",
      "options": {
        "cacheableOperations": ["build", "test", "lint"]
      }
    }
  },
  "targetDefaults": {
    "build": {
      "dependsOn": ["^build"]
    }
  }
}
```

**Nx 常用命令**：

```bash
# 构建受影响的项目（基于 git diff）
nx affected:build

# 测试受影响的项目
nx affected:test

# 查看依赖图（浏览器可视化）
nx graph

# 启动 admin-web（自动处理依赖）
nx serve admin-web

# 运行单个任务
nx run admin-web:build
nx run ui:test

# 并行运行多个任务
nx run-many --target=build --projects=admin-web,user-web

# 代码生成
nx g component Button --project=ui
```

### 4.5 Lerna（传统方案）

**定位**：老牌 Monorepo 工具（v6+ 后集成了 Nx）

#### 特点
- 版本管理（lerna version）
- 发布管理（lerna publish）
- 版本打 CHANGELOG
- 依赖 bootstrap

**适用场景**：需要多包独立版本发布的开源项目

```json
// lerna.json
{
  "$schema": "node_modules/lerna/schemas/lerna-schema.json",
  "version": "independent",  // 独立版本模式
  "npmClient": "pnpm",
  "useWorkspaces": true,
  "packages": ["packages/*"]
}
```

```bash
# 安装依赖（传统 Lerna 用法，现在建议直接用 pnpm）
lerna bootstrap

# 查看包版本
lerna ls

# 版本发布（自动处理 CHANGELOG、Git tag）
lerna version

# 发布到 npm
lerna publish
```

### 4.6 方案选择建议

```
┌─────────────────────────────────────────────────────────────────────┐
│                       Monorepo 工具选型建议                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  小型项目 / 学习用：                                                 │
│  └── pnpm Workspace（简单够用）                                     │
│                                                                     │
│  中型项目（Vue/Vite 生态）：                                         │
│  └── pnpm Workspace + Turborepo（目前社区主流方案）                 │
│                                                                     │
│  中型项目（React/Next 生态）：                                       │
│  └── pnpm Workspace + Turborepo（Vercel 官方推荐）                  │
│                                                                     │
│  大型企业项目（需要代码生成、可视化）：                               │
│  └── pnpm Workspace + Nx（企业级特性）                              │
│                                                                     │
│  开源多包项目（需要独立发布）：                                      │
│  └── pnpm Workspace + Changesets（版本管理） + Turborepo（构建）    │
│                                                                     │
│  超大型项目（语言混合、千包级别）：                                   │
│  └── pnpm Workspace + Bazel（极致性能）或 Rush（微软方案）          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**当前社区最推荐方案**：**pnpm Workspace + Turborepo + Changesets**

---

## 五、项目结构设计原则

### 5.1 目录结构规范

#### 标准结构

```
my-monorepo/
├── apps/                          ← 可部署的应用
│   ├── admin-web/               ← 管理后台
│   │   ├── src/
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── vite.config.ts
│   │   └── README.md
│   ├── user-web/                ← 用户端
│   └── docs/                    ← 文档站点
│
├── packages/                      ← 可复用的包
│   ├── ui/                      ← UI 组件库
│   │   ├── src/
│   │   │   ├── components/
│   │   │   └── index.ts
│   │   ├── package.json         ← name: @company/ui
│   │   └── build.config.ts
│   │
│   ├── utils/                   ← 工具函数库
│   │   ├── src/
│   │   │   ├── date.ts
│   │   │   ├── string.ts
│   │   │   └── index.ts
│   │   └── package.json         ← name: @company/utils
│   │
│   ├── api-client/              ← API 请求客户端
│   │   ├── src/
│   │   │   ├── request.ts
│   │   │   └── modules/
│   │   └── package.json         ← name: @company/api-client
│   │
│   ├── types/                   ← 共享类型定义
│   │   ├── src/
│   │   │   ├── user.ts
│   │   │   ├── product.ts
│   │   │   └── index.ts
│   │   └── package.json         ← name: @company/types
│   │
│   └── config/                  ← 配置包（统一配置）
│       ├── eslint-config/       ← 共享 eslint 配置
│       ├── tsconfig/            ← 共享 tsconfig
│       └── prettier-config/     ← 共享 prettier 配置
│
├── tooling/                       ← 内部工具脚本
│   └── scripts/
│
├── .github/                       ← GitHub 配置
│   ├── workflows/               ← CI 流水线
│   └── CODEOWNERS               ← 代码所有者（权限控制）
│
├── tests/                         ← E2E 测试、集成测试
│
├── docs/                          ← 项目文档（架构、规范）
│   ├── architecture.md
│   ├── development.md
│   └── deployment.md
│
├── package.json                   ← 根配置
├── pnpm-workspace.yaml          ← pnpm workspace
├── turbo.json                     ← Turborepo 配置
├── tsconfig.base.json             ← 共享 TS 基础配置
├── tsconfig.json                  ← 根 TS 配置
├── .eslintrc.cjs                  ← ESLint
├── .prettierrc                    ← Prettier
├── .gitignore
├── .npmrc                         ← npm/pnpm 配置
├── .editorconfig
├── CHANGELOG.md
└── README.md
```

### 5.2 包命名规范

```
命名规则：@scope/package-name

示例：
@company/admin-web        应用
@company/user-web         应用
@company/ui               UI 组件库
@company/utils            工具库
@company/api-client       API 客户端
@company/types            类型定义
@company/eslint-config    配置包

优点：
1. 避免 npm 包名冲突
2. 一眼看出所属组织
3. 内部包命名统一
```

### 5.3 分层原则

```
┌─────────────────────────────────────────────────────────────────────┐
│                      包的分层依赖关系（单向）                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  第 4 层：应用层（apps/）                 不能被其他层依赖          │
│  ├── admin-web                                                   │
│  ├── user-web                                                    │
│  └── docs                                                        │
│         │                                                         │
│         │ 引用                                                    │
│         ▼                                                         │
│  第 3 层：业务层（packages/）              可被应用层依赖          │
│  ├── api-client（API 封装）                                      │
│  ├── business-components（业务组件）                             │
│         │                                                         │
│         │ 引用                                                    │
│         ▼                                                         │
│  第 2 层：通用层（packages/）              可被上层依赖            │
│  ├── ui（通用 UI 组件）                                          │
│  ├── hooks（通用 Composables）                                   │
│         │                                                         │
│         │ 引用                                                    │
│         ▼                                                         │
│  第 1 层：基础层（packages/）              只能内部自依赖          │
│  ├── types（类型定义）                                           │
│  ├── utils（纯函数工具）                                         │
│  └── config（基础配置）                                          │
│                                                                     │
│  依赖方向：高层 → 低层（单向，禁止循环依赖）                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**包之间引用示例**：

```json
// apps/admin-web/package.json
{
  "name": "@company/admin-web",
  "dependencies": {
    "@company/ui": "workspace:*",          // 第2层
    "@company/api-client": "workspace:*",  // 第3层
    "@company/types": "workspace:*",       // 第1层
    "@company/utils": "workspace:*"        // 第1层
  }
}

// packages/api-client/package.json
{
  "name": "@company/api-client",
  "dependencies": {
    "@company/types": "workspace:*",       // 第1层（正确：低层）
    "@company/utils": "workspace:*"        // 第1层（正确：低层）
    // ❌ 不能引用 @company/admin-web（应用层，高层）
    // ❌ 不能引用 @company/ui（同层非基础，需看情况）
  }
}

// packages/utils/package.json
{
  "name": "@company/utils"
  // 基础层，不能依赖任何上层
}
```

### 5.4 配置继承设计

```
TypeScript 配置继承链：

┌──────────────────────────────────────────────────────────┐
│ tsconfig.base.json (根目录，公共基础配置)                │
│ {                                                        │
│   "compilerOptions": {                                   │
│     "target": "ES2020",                                  │
│     "module": "ESNext",                                  │
│     "strict": true,                                      │
│     "esModuleInterop": true,                             │
│     "skipLibCheck": true                                 │
│   }                                                      │
│ }                                                        │
└──────────────────────────────┬───────────────────────────┘
                               │ extends
                               ▼
┌──────────────────────────────────────────────────────────┐
│ packages/ui/tsconfig.json                                │
│ {                                                        │
│   "extends": "../../tsconfig.base.json",                 │
│   "compilerOptions": {                                   │
│     "outDir": "./dist",                                  │
│     "rootDir": "./src",                                  │
│     "types": ["vue"]                                     │
│   },                                                     │
│   "include": ["src/**/*.ts", "src/**/*.vue"]             │
│ }                                                        │
└──────────────────────────────────────────────────────────┘
```

```
ESLint 配置继承：

// packages/config/eslint-config/index.cjs
module.exports = {
  root: true,
  env: { browser: true, node: true, es2022: true },
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: '@typescript-eslint/parser',
    sourceType: 'module'
  },
  rules: {
    // 团队统一规则
  }
}

// apps/admin-web/.eslintrc.cjs
module.exports = {
  extends: ['@company/eslint-config']  // 继承公共配置
}
```

---

## 六、依赖管理策略

### 6.1 依赖分类

| 依赖类型 | 说明 | 放在哪里 | 示例 |
|---------|------|---------|------|
| **公共 devDependencies** | 所有包都需要的开发依赖 | 根 package.json | typescript, eslint, prettier |
| **公共 dependencies** | 所有包都需要的运行时依赖（极少） | 根 package.json | vue, react |
| **包自身 devDependencies** | 特定包需要的开发依赖 | 各包 package.json | vite, vitest, rollup |
| **包自身 dependencies** | 特定包运行时需要的依赖 | 各包 package.json | element-plus, axios |
| **peerDependencies** | 包对宿主环境的要求（让使用者安装） | 各包 package.json | vue: ^3.0.0 |

### 6.2 依赖提升与隔离

#### pnpm 依赖提升策略

```
pnpm 依赖结构（硬链接 + 符号链接）：

node_modules/
├── .pnpm/                      ← 所有包的真实存储（pnpm store）
│   ├── vue@3.3.4/
│   │   └── node_modules/
│   │       └── vue → 真实文件（硬链接到 store）
│   ├── element-plus@2.3.8/
│   └── ...
│
├── vue → ./.pnpm/vue@3.3.4/node_modules/vue  ← 符号链接（提升到根）
├── element-plus                              ← 提升到根（如果多个包用到）
│
packages/
  ├── admin-web/
  │   └── node_modules/
  │       └── @company/
  │           └── ui → ../../../ui  ← workspace 引用，链接到本地源码
  │
  └── ui/
      └── node_modules/
          └── element-plus → ../../node_modules/.pnpm/element-plus@...
```

#### 幻影依赖（Phantom Dependencies）

```javascript
// ❌ 错误：使用了未声明的依赖
// packages/admin-web/src/main.ts
import dayjs from 'dayjs'
// 但 admin-web/package.json 没有声明 dayjs
// 只是因为根目录或其他包安装了 dayjs 才侥幸能用

// ✅ 正确：每个包都声明自己的依赖
// packages/admin-web/package.json
{
  "dependencies": {
    "dayjs": "^1.11.0"  // 显式声明
  }
}
```

**pnpm 防止幻影依赖的配置**：

```ini
# .npmrc
shamefully-hoist=false   # 不将所有依赖提升到根（默认 false）
hoist-pattern[]=*vue*   # 可选：允许特定模式的依赖提升
strict-peer-dependencies=false
```

### 6.3 workspace 协议

pnpm 提供了 workspace 协议，让包之间互相引用时始终指向本地最新代码：

```json
// packages/admin-web/package.json
{
  "dependencies": {
    "@company/ui": "workspace:*",      // 始终使用本地最新版本
    "@company/utils": "workspace:^",   // 遵循 semver（发布时转换为 ^x.x.x）
    "@company/types": "workspace:~1.0.0" // 发布时转换为 ~1.0.0
  }
}
```

**发布时转换**：

```json
// 开发时（本地）
{
  "@company/ui": "workspace:*"
}

// 发布到 npm 后（pnpm publish 自动转换）
{
  "@company/ui": "^1.2.3"
}
```

### 6.4 版本管理方案

#### 方案一：固定版本（Single Version Policy）

```json
// 所有包使用相同版本号
// package.json
{
  "version": "1.5.0"
}

// packages/ui/package.json
{
  "name": "@company/ui",
  "version": "1.5.0"
}

// packages/utils/package.json
{
  "name": "@company/utils",
  "version": "1.5.0"
}

优点：版本管理简单，所有包同步升级
缺点：小改动也会升级所有包版本
```

#### 方案二：独立版本（Independent Mode）

```json
// 每个包独立维护版本号
// packages/ui/package.json
{
  "name": "@company/ui",
  "version": "2.1.0"
}

// packages/utils/package.json
{
  "name": "@company/utils",
  "version": "1.3.5"
}

优点：灵活，小改动小升级
缺点：依赖关系管理复杂

推荐工具：Changesets
```

#### Changesets（版本管理工具）

```bash
# 安装
pnpm add -Dw @changesets/cli
npx changeset init

# 开发者提交改动说明
npx changeset

# 消耗 changesets，更新版本号和 CHANGELOG
npx changeset version

# 发布
pnpm -r publish
```

Changesets 工作流程：

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Changesets 工作流程                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. 开发完成 → npx changeset                                        │
│     选择变更包 → 选择版本类型(patch/minor/major) → 填写变更说明     │
│     生成 .changeset/xxx.md（提交到 Git）                           │
│                        ↓                                            │
│  2. 合并 PR 到主分支                                                │
│     CI 执行 npx changeset version                                  │
│     - 读取 .changeset/ 下的文件                                     │
│     - 自动更新各包 package.json 的 version                          │
│     - 自动生成/追加 CHANGELOG.md                                    │
│     - 删除已消耗的 changeset 文件                                   │
│     - 创建 Release PR                                               │
│                        ↓                                            │
│  3. 合并 Release PR                                                 │
│     CI 执行 pnpm -r publish                                        │
│     发布到 npm 仓库                                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.5 常见依赖问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **循环依赖** | A 依赖 B，B 依赖 A | 重构代码，提取公共部分到 C |
| **幻影依赖** | 未声明依赖但实际使用 | 开启 pnpm 严格模式，CI 检查 |
| **doppelgangers** | 同个依赖多个版本 | 统一版本，使用 overrides 强制版本 |
| **peer 依赖冲突** | 不同包要求的 peer 版本不一致 | 统一版本，或调整包设计 |
| **本地包引用不生效** | workspace 配置错误 | 检查 pnpm-workspace.yaml，用 workspace:* |

**强制统一版本**：

```json
// package.json（根目录）
{
  "pnpm": {
    "overrides": {
      // 强制所有包使用同一个 vue 版本
      "vue": "3.3.4",
      // 强制所有 lodash 升级
      "lodash": "4.17.21",
      // 特定包的依赖
      "@company/api-client>axios": "1.5.0"
    }
  }
}
```

---

## 七、构建与部署流程

### 7.1 增量构建流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                    增量构建 + 缓存流程（Turborepo）                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  代码变更（git diff）                                               │
│        ↓                                                             │
│  1. 计算输入哈希（turbo hash）                                      │
│     - 源文件内容哈希                                                │
│     - 依赖项构建哈希                                                │
│     - 全局配置文件哈希（如 tsconfig）                               │
│     - 环境变量哈希                                                  │
│        ↓                                                             │
│  2. 查询本地缓存：.turbo/cache/<hash>                               │
│     ├── 命中 → 解压产物，跳过构建（秒级完成）                       │
│     └── 未命中 → 继续步骤 3                                         │
│        ↓                                                             │
│  3. 查询远程缓存（可选）                                            │
│     ├── 命中 → 下载产物，写入本地缓存                              │
│     └── 未命中 → 继续步骤 4                                         │
│        ↓                                                             │
│  4. 执行实际构建                                                    │
│     - 按依赖拓扑排序                                                 │
│     - 并行构建无依赖关系的包                                        │
│        ↓                                                             │
│  5. 写入缓存（本地 + 远程）                                         │
│     下次同样输入直接命中缓存                                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.2 CI/CD 流水线设计

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  setup:
    name: Setup
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 20  # 受影响分析需要 git history

      - uses: pnpm/action-setup@v2
        with:
          version: 8

      - uses: actions/setup-node@v3
        with:
          node-version: 18
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

  lint:
    name: Lint
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/cache@v3
        with:
          path: |
            .turbo
            node_modules/.cache/turbo
          key: turbo-${{ github.sha }}
          restore-keys: turbo-
      - run: pnpm install
      - run: pnpm lint

  test:
    name: Test
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/cache@v3
        with:
          path: .turbo
          key: turbo-test-${{ github.sha }}
          restore-keys: turbo-test-
      - run: pnpm install
      - run: pnpm test

  build:
    name: Build
    needs: [lint, test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/cache@v3
        with:
          path: .turbo
          key: turbo-build-${{ github.sha }}
          restore-keys: turbo-build-

      - name: Setup Turbo Remote Cache
        env:
          TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
          TURBO_TEAM: ${{ secrets.TURBO_TEAM }}
        run: echo "Turbo configured"

      - run: pnpm install
      - run: pnpm build  # turbo build 自动增量 + 远程缓存

  deploy-admin-web:
    name: Deploy Admin Web
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/download-artifact@v3
        with:
          name: admin-web-dist
          path: apps/admin-web/dist
      - name: Deploy to Vercel
        run: vercel deploy --prod --token ${{ secrets.VERCEL_TOKEN }}
```

### 7.3 包的构建配置（以 UI 组件库为例）

```typescript
// packages/ui/vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import dts from 'vite-plugin-dts'  // 自动生成 .d.ts 类型声明
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue(),
    dts({
      insertTypesEntry: true,
      outDir: 'dist/types'
    })
  ],
  build: {
    lib: {
      entry: resolve(__dirname, 'src/index.ts'),
      name: 'CompanyUI',
      formats: ['es', 'umd', 'cjs'],
      fileName: (format) => `company-ui.${format}.js`
    },
    rollupOptions: {
      // 将 vue 视为外部依赖，不打包进去
      external: ['vue', 'element-plus'],
      output: {
        globals: {
          vue: 'Vue',
          'element-plus': 'ElementPlus'
        }
      }
    }
  }
})
```

```json
// packages/ui/package.json
{
  "name": "@company/ui",
  "version": "1.0.0",
  "type": "module",
  "main": "./dist/company-ui.cjs.js",
  "module": "./dist/company-ui.es.js",
  "types": "./dist/types/index.d.ts",
  "files": ["dist"],
  "exports": {
    ".": {
      "import": "./dist/company-ui.es.js",
      "require": "./dist/company-ui.cjs.js",
      "types": "./dist/types/index.d.ts"
    },
    "./style.css": "./dist/style.css"
  },
  "scripts": {
    "build": "vite build",
    "test": "vitest run"
  },
  "peerDependencies": {
    "vue": "^3.3.0",
    "element-plus": "^2.3.0"
  }
}
```

### 7.4 部署流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Monorepo 部署流程                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  方式一：独立部署（推荐，各自独立）                                  │
│                                                                     │
│  admin-web 变更 → CI 构建 admin-web + 依赖 → 部署到 A 服务器       │
│  user-web 变更  → CI 构建 user-web  + 依赖 → 部署到 B 服务器       │
│  ui 包 变更    → CI 构建所有依赖 ui 的应用 → 全部部署                │
│                                                                     │
│  方式二：统一部署（小项目简单）                                      │
│                                                                     │
│  任何变更 → 构建所有项目 → 统一部署到对应的服务器                   │
│                                                                     │
│  方式三：Docker 镜像                                                │
│                                                                     │
│  apps/admin-web/Dockerfile                                          │
│  apps/user-web/Dockerfile                                           │
│  构建时自动构建对应的 Docker 镜像 → 推送到镜像仓库 → K8s 部署      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 八、pnpm + Turborepo 实战配置

### 8.1 从零搭建 Monorepo

```bash
# 1. 创建项目目录
mkdir my-monorepo
cd my-monorepo
git init

# 2. 初始化 package.json
pnpm init

# 3. 修改根 package.json
# （见下方示例）

# 4. 创建 pnpm-workspace.yaml
# （见下方示例）

# 5. 创建 turbo.json
# （见下方示例）

# 6. 创建共享配置文件（tsconfig, eslint, prettier）

# 7. 创建子包
mkdir -p packages/ui packages/utils packages/types
mkdir -p apps/admin-web apps/docs

# 8. 初始化各子包
cd packages/utils
pnpm init
# ... 配置各 package.json
```

### 8.2 根配置文件

```jsonc
// package.json（根）
{
  "name": "my-monorepo",
  "version": "0.0.0",
  "private": true,
  "packageManager": "pnpm@8.6.0",
  "engines": {
    "node": ">=18.0.0",
    "pnpm": ">=8.0.0"
  },
  "scripts": {
    // Turbo 脚本
    "dev": "turbo run dev",
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "clean": "turbo run clean && rm -rf node_modules",

    // pnpm 直接脚本
    "dev:admin": "pnpm -F @company/admin-web dev",
    "dev:user": "pnpm -F @company/user-web dev",
    "build:ui": "pnpm -F @company/ui build",

    // 工具脚本
    "format": "prettier --write \"**/*.{ts,vue,json,md}\"",
    "typecheck": "turbo run typecheck",
    "changeset": "changeset",
    "release": "changeset version && pnpm build && pnpm -r publish"
  },
  "devDependencies": {
    "turbo": "^1.10.0",
    "typescript": "^5.1.0",
    "eslint": "^8.44.0",
    "prettier": "^2.8.8",
    "@changesets/cli": "^2.26.0",
    "vue-eslint-parser": "^9.3.0",
    "@typescript-eslint/parser": "^5.61.0",
    "@typescript-eslint/eslint-plugin": "^5.61.0"
  },
  "pnpm": {
    "overrides": {
      "vue": "3.3.4"
    },
    "peerDependencyRules": {
      "ignoreMissing": ["vite", "vue"]
    }
  }
}
```

```yaml
# pnpm-workspace.yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": [
    "tsconfig.base.json",
    "tsconfig.json",
    ".eslintrc.cjs",
    ".prettierrc",
    ".npmrc"
  ],
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [
        "dist/**",
        "build/**",
        ".next/**",
        "!.next/cache/**",
        "types/**"
      ],
      "outputMode": "new-only",
      "cache": true
    },
    "dev": {
      "dependsOn": ["^build"],
      "cache": false,
      "persistent": true
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**", "test-report/**"],
      "cache": true
    },
    "lint": {
      "outputs": [],
      "cache": true
    },
    "typecheck": {
      "dependsOn": ["^build"],
      "outputs": [],
      "cache": true
    },
    "clean": {
      "cache": false
    }
  }
}
```

```jsonc
// tsconfig.base.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "moduleResolution": "Node",
    "strict": true,
    "jsx": "preserve",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "baseUrl": ".",
    "paths": {
      "@company/ui": ["packages/ui/src"],
      "@company/utils": ["packages/utils/src"],
      "@company/types": ["packages/types/src"],
      "@company/api-client": ["packages/api-client/src"]
    }
  }
}
```

```jsonc
// tsconfig.json（根，不编译只是为了 IDE）
{
  "files": [],
  "references": [
    { "path": "./packages/ui" },
    { "path": "./packages/utils" },
    { "path": "./packages/types" },
    { "path": "./packages/api-client" },
    { "path": "./apps/admin-web" }
  ]
}
```

```javascript
// .eslintrc.cjs
module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
    es2022: true
  },
  extends: [
    'eslint:recommended'
  ],
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: '@typescript-eslint/parser',
    sourceType: 'module'
  },
  rules: {
    'no-unused-vars': 'warn',
    'no-console': ['warn', { allow: ['warn', 'error'] }]
  },
  ignorePatterns: ['dist', 'node_modules', 'coverage']
}
```

```json
// .prettierrc
{
  "semi": false,
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "trailingComma": "none",
  "arrowParens": "always",
  "endOfLine": "lf"
}
```

```ini
# .npmrc
shamefully-hoist=false
strict-peer-dependencies=false
auto-install-peers=true
link-workspace-packages=true
prefer-workspace-packages=true
```

```gitignore
# .gitignore
node_modules
dist
build
.turbo
.cache
coverage
*.log
.DS_Store
.env
.env.local
.vscode/*
!.vscode/extensions.json
.idea
```

### 8.3 各子包配置示例

#### packages/types（类型包）

```json
// packages/types/package.json
{
  "name": "@company/types",
  "version": "1.0.0",
  "type": "module",
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "publishConfig": {
    "main": "./dist/index.cjs",
    "module": "./dist/index.js",
    "types": "./dist/index.d.ts"
  },
  "exports": {
    ".": {
      "types": "./src/index.ts",
      "development": "./src/index.ts",
      "default": "./dist/index.js"
    }
  },
  "scripts": {
    "build": "tsc --build",
    "typecheck": "tsc --noEmit"
  },
  "devDependencies": {
    "typescript": "^5.0.0"
  }
}
```

```typescript
// packages/types/src/index.ts
export interface User {
  id: number
  name: string
  email: string
  avatar?: string
  role: 'admin' | 'user' | 'guest'
  createdAt: Date
}

export interface Product {
  id: number
  name: string
  price: number
  description: string
  stock: number
  images: string[]
}

export interface PaginationParams {
  page: number
  pageSize: number
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

export interface PaginatedResult<T> {
  data: T[]
  total: number
  page: number
  pageSize: number
}
```

```json
// packages/types/tsconfig.json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src",
    "composite": true
  },
  "include": ["src/**/*.ts"]
}
```

#### packages/utils（工具函数包）

```json
// packages/utils/package.json
{
  "name": "@company/utils",
  "version": "1.0.0",
  "type": "module",
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "scripts": {
    "build": "tsc --build",
    "test": "vitest run",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@company/types": "workspace:*",
    "dayjs": "^1.11.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "vitest": "^0.33.0"
  }
}
```

```typescript
// packages/utils/src/format.ts
import type { User } from '@company/types'
import dayjs from 'dayjs'

/**
 * 格式化日期
 */
export function formatDate(date: Date | string | number, format: string = 'YYYY-MM-DD HH:mm:ss'): string {
  return dayjs(date).format(format)
}

/**
 * 格式化金额
 */
export function formatCurrency(amount: number, currency: string = 'CNY'): string {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2
  }).format(amount)
}

/**
 * 格式化用户信息
 */
export function formatUserDisplay(user: User): string {
  return `${user.name} (${user.role})`
}
```

```typescript
// packages/utils/src/validate.ts
/**
 * 验证邮箱格式
 */
export function isEmail(value: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return regex.test(value)
}

/**
 * 验证手机号（中国）
 */
export function isMobilePhone(value: string): boolean {
  const regex = /^1[3-9]\d{9}$/
  return regex.test(value)
}

/**
 * 验证是否为有效 ID
 */
export function isValidId(value: unknown): value is number | string {
  if (typeof value === 'number') return value > 0
  if (typeof value === 'string') return value.trim().length > 0
  return false
}
```

```typescript
// packages/utils/src/index.ts
export * from './format'
export * from './validate'
```

#### packages/ui（组件库包）

```json
// packages/ui/package.json
{
  "name": "@company/ui",
  "version": "1.0.0",
  "type": "module",
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "scripts": {
    "build": "vite build",
    "dev": "vite build --watch",
    "test": "vitest run",
    "typecheck": "vue-tsc --noEmit"
  },
  "dependencies": {
    "@company/utils": "workspace:*",
    "@company/types": "workspace:*",
    "element-plus": "^2.3.0"
  },
  "peerDependencies": {
    "vue": "^3.3.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.2.0",
    "typescript": "^5.0.0",
    "vite": "^4.3.0",
    "vite-plugin-dts": "^2.3.0",
    "vue": "^3.3.0",
    "vue-tsc": "^1.8.0"
  }
}
```

```vue
<!-- packages/ui/src/components/UserCard.vue -->
<template>
  <el-card class="user-card">
    <div class="user-info">
      <el-avatar :size="60" :src="user.avatar">
        {{ user.name?.charAt(0) }}
      </el-avatar>
      <div class="user-details">
        <h3 class="user-name">{{ user.name }}</h3>
        <p class="user-email">{{ user.email }}</p>
        <el-tag :type="roleTagType">{{ formatRole }}</el-tag>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { User } from '@company/types'
import { formatDate } from '@company/utils'

interface Props {
  user: User
}

const props = defineProps<Props>()

const formatRole = computed(() => {
  const roleMap: Record<User['role'], string> = {
    admin: '管理员',
    user: '普通用户',
    guest: '访客'
  }
  return roleMap[props.user.role]
})

const roleTagType = computed(() => {
  const typeMap: Record<User['role'], string> = {
    admin: 'danger',
    user: 'primary',
    guest: 'info'
  }
  return typeMap[props.user.role]
})

// 暴露方法
defineExpose({
  formatDate
})
</script>

<style scoped>
.user-card {
  width: 320px;
}

.user-info {
  display: flex;
  gap: 16px;
  align-items: center;
}

.user-details {
  flex: 1;
}

.user-name {
  margin: 0 0 4px;
  font-size: 16px;
}

.user-email {
  margin: 0 0 8px;
  color: #909399;
  font-size: 13px;
}
</style>
```

```typescript
// packages/ui/src/index.ts
import type { App } from 'vue'
import UserCard from './components/UserCard.vue'

// 单独导出组件
export { UserCard }

// 支持全局注册（app.use）
export function install(app: App): void {
  app.component('UserCard', UserCard)
}

export default { install }
```

#### apps/admin-web（管理后台应用）

```json
// apps/admin-web/package.json
{
  "name": "@company/admin-web",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc --noEmit && vite build",
    "preview": "vite preview",
    "lint": "eslint src/**/*.{ts,vue}",
    "typecheck": "vue-tsc --noEmit"
  },
  "dependencies": {
    "@company/ui": "workspace:*",
    "@company/utils": "workspace:*",
    "@company/types": "workspace:*",
    "@company/api-client": "workspace:*",
    "vue": "^3.3.4",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "element-plus": "^2.3.0",
    "axios": "^1.4.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.2.0",
    "typescript": "^5.0.0",
    "vite": "^4.3.0",
    "vue-tsc": "^1.8.0"
  }
}
```

```typescript
// apps/admin-web/vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      // 开发时引用 workspace 包源码，支持 HMR
      '@company/ui': resolve(__dirname, '../../packages/ui/src'),
      '@company/utils': resolve(__dirname, '../../packages/utils/src'),
      '@company/types': resolve(__dirname, '../../packages/types/src')
    }
  },
  server: {
    port: 3000,
    host: true
  },
  build: {
    outDir: 'dist',
    sourcemap: false
  }
})
```

```typescript
// apps/admin-web/src/main.ts
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import CompanyUI from '@company/ui'

const app = createApp(App)

app.use(ElementPlus)
app.use(createPinia())
app.use(router)
app.use(CompanyUI)  // 注册全局 UI 组件

app.mount('#app')
```

```vue
<!-- apps/admin-web/src/views/Users.vue -->
<template>
  <div class="users-page">
    <h1>用户管理</h1>
    <div class="user-list">
      <UserCard
        v-for="user in users"
        :key="user.id"
        :user="user"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { User } from '@company/types'
import UserCard from '@company/ui'

const users = ref<User[]>([])

onMounted(async () => {
  // 调用 API（workspace 包）
  // import { userApi } from '@company/api-client'
  // users.value = await userApi.list()
})
</script>
```

### 8.4 项目验证

```bash
# 安装依赖
pnpm install

# 查看 workspace 结构
pnpm ls -r --depth -1

# 检查依赖关系（Turborepo）
turbo build --dry=json

# 启动管理后台（自动先构建依赖包）
pnpm dev:admin
# 或
turbo dev --filter=@company/admin-web

# 构建所有包
pnpm build

# 清理构建产物
pnpm clean
```

---

## 九、最佳实践与注意事项

### 9.1 项目启动清单

创建 Monorepo 项目时检查以下项：

- [ ] **包管理器选择**：使用 pnpm（推荐），在 package.json 指定 `"packageManager"`
- [ ] **工作区配置**：pnpm-workspace.yaml 正确配置所有包路径
- [ ] **根 package.json**：设为 `"private": true`，脚本使用 turbo 或 pnpm -r
- [ ] **包命名规范**：使用 `@scope/package-name` 统一命名
- [ ] **分层结构**：apps/ 和 packages/ 分离，单向依赖
- [ ] **公共配置**：tsconfig.base.json、eslint、prettier 在根目录
- [ ] **依赖声明**：每个包显式声明 dependencies，避免幻影依赖
- [ ] **本地引用**：使用 `workspace:*` 协议引用内部包
- [ ] **构建配置**：Turborepo/Nx 配置缓存任务（build/test/lint）
- [ ] **版本管理**：使用 Changesets 管理版本和发布
- [ ] **CI 配置**：GitHub Actions/GitLab CI 集成缓存
- [ ] **Git 规范**：.gitignore、commitlint、lint-staged、Husky
- [ ] **说明文档**：README.md 说明目录结构、开发流程、构建命令

### 9.2 性能优化建议

| 优化方向 | 具体措施 |
|---------|---------|
| **安装速度** | 使用 pnpm，开启 pre-post scripts 缓存，配置 registry 镜像 |
| **磁盘占用** | pnpm store prune，定期清理，使用硬链接去重 |
| **本地构建** | Turborepo 本地缓存，增量构建（--filter） |
| **团队构建** | Turborepo 远程缓存，CI 与本地共享缓存 |
| **冷启动开发** | 不使用 `--parallel` 启动所有应用，只 `--filter` 需要的 |
| **TypeScript** | 使用 Project References（tsc --build）增量编译 |
| **Git 体积** | 大文件用 Git LFS，使用 shallow clone（git clone --depth=1） |
| **Docker 构建** | 多阶段构建，只 COPY package.json 先装依赖层缓存 |

### 9.3 Git 工作流

```
推荐：Trunk-Based Development（主干开发）

        main（受保护分支，禁止直接 push）
         │
         │  feature-xxx 分支开发
         │  1. 拉新分支：git checkout -b feature/add-xxx
         │  2. 开发 + 提交（每个包改动尽量独立 PR）
         │  3. 提交 PR
         │     - 自动 lint、test、affected build
         │     - Code Review
         │  4. Squash Merge 合并到 main
         │
         ▼
    main 更新 → 触发 Release 流程 → 自动发版
```

**Commit 规范（Conventional Commits）**：

```
feat(ui): Button 新增 size 属性
fix(utils): 修复 formatDate 边界 case
docs: 更新 README 安装说明
chore: 升级 vue 到 3.3.4
refactor(api-client): 重构请求拦截器
test: 补充 UserCard 单测
```

**PR 模板**：

```
## 变更类型
- [ ] Feature（新功能）
- [ ] Bugfix（修复）
- [ ] Docs（文档）
- [ ] Refactor（重构）
- [ ] Chore（工具/配置）
- [ ] Test（测试）

## 影响范围
- 涉及包：@company/ui, @company/admin
- 受影响的其他包：
- 是否需要发布：是 / 否

## 自测项
- [ ] 本地 lint 通过
- [ ] 本地 test 通过
- [ ] 本地 build 通过
- [ ] 受影响包全部构建通过
- [ ] 本地启动验证

## 说明
...
```

### 9.4 代码所有权（CODEOWNERS）

```
# .github/CODEOWNERS

# 根级配置和文档
*                                       @company/admin

# 架构团队审核配置
/package.json                           @company/admin/architects
/pnpm-workspace.yaml                    @company/admin/architects
/turbo.json                             @company/admin/architects
/.github/workflows/                     @company/admin/architects

# 团队分包负责
/apps/admin-web/                        @company/admin/admin-team
/apps/admin-web/src/views/order/       @company/admin/order-team

/packages/ui/                           @company/admin/design-system
/packages/utils/                        @company/admin/design-system
/packages/api-client/                   @company/admin/api-team

# 文档由文档团队负责
/docs/                                  @company/docs-team
```

### 9.5 常见错误与排查

#### 错误 1：workspace 包引用找不到类型

```
错误：Cannot find module '@company/ui' or its corresponding type declarations.
```

**排查**：
1. 检查 pnpm-workspace.yaml 是否包含该包路径
2. 检查包 package.json 的 name 是否正确
3. 检查引用方是否正确 `pnpm -F admin-web add @company/ui@workspace:*`
4. 检查 tsconfig paths 是否映射正确
5. 运行 `pnpm install` 重新链接

#### 错误 2：Turborepo 任务不按顺序执行

```
错误：admin-web build 报错找不到 @company/ui/dist
```

**排查**：
1. 检查 turbo.json 的 build 任务是否 `"dependsOn": ["^build"]`
2. 检查 admin-web/package.json 是否声明了对 @company/ui 的依赖
3. 检查 @company/ui/package.json 是否有 build 脚本
4. 用 `turbo build --dry=text --graph=graph.html` 可视化依赖图

#### 错误 3：循环依赖

```
错误：Circular dependency: @company/admin → @company/ui → @company/admin
```

**排查**：
1. 画依赖图：`turbo run build --graph`
2. 找到循环点，提取公共代码到第三个包
3. 用 ESLint 规则禁止循环导入：`import/no-cycle`

```javascript
// .eslintrc.cjs 规则
{
  rules: {
    'import/no-cycle': ['error', { maxDepth: 3 }]
  }
}
```

#### 错误 4：同一个依赖安装了多份

```
错误：[Vue warn]: The client-side rendered virtual DOM tree is not matching server-rendered content.
（多份 Vue 实例）
```

**排查**：
1. `pnpm why vue` 查看所有 vue 安装路径
2. 在根 package.json 配置 `pnpm.overrides` 强制统一版本
3. `pnpm dedupe` 去重

#### 错误 5：Turborepo 缓存没命中

**排查**：
1. 检查 turbo.json 的 inputs 是否正确（过宽会 hash 不一致，过窄会漏）
2. 检查 globalDependencies 是否包含公共配置
3. 用 `turbo build --verbosity=3` 查看 hash 计算细节
4. 确保 CI 环境还原 .turbo 目录（actions/cache）

---

## 十、常见问题 FAQ

### Q1: Monorepo 是不是适合所有项目？

**A**: 不是。
- ✅ 适合：多项目紧密协作、大量共享代码、统一规范团队
- ❌ 不适合：完全独立的项目、安全隔离要求极高、超大规模无工具支撑

### Q2: Monorepo 和 Monolith（单体应用）有什么区别？

**A**: 
- **Monorepo**：代码组织方式（一个 Git 仓库多个包），部署可以是多个独立应用
- **Monolith**：部署架构（所有功能打包为一个部署单元）
- Monorepo 可以部署为 Monolith，也可以部署为多个独立服务

### Q3: pnpm、npm、yarn 哪个更适合 Monorepo？

**A**: 目前社区公认 **pnpm** 最佳：
- 依赖管理最严格（防止幻影依赖）
- 磁盘占用最小（硬链接去重）
- 安装速度最快
- workspace 功能最完善

### Q4: Turborepo 和 Nx 选哪个？

**A**: 
- **Turborepo**：轻量、与 Vite/Next 生态契合、配置简单，适合中小型项目和 Vue 项目
- **Nx**：功能全、代码生成、可视化、企业级特性，适合大型企业和 Angular/React 项目

### Q5: Monorepo 中如何处理大型二进制文件？

**A**: 使用 Git LFS（Large File Storage）：
```bash
# 安装 Git LFS
git lfs install

# 追踪大文件类型
git lfs track "*.psd"
git lfs track "packages/assets/**/*.png"

# 提交 .gitattributes
git add .gitattributes
```

### Q6: Monorepo 中每个应用可以用不同的框架吗？

**A**: 可以！Monorepo 不限制技术栈：
```
packages/
├── admin-web/        Vue + Element Plus
├── user-web/         React + Ant Design
├── mobile-app/       React Native
├── mini-program/     UniApp
└── admin-server/     NestJS

共享：
├── ui/               （只提供设计 token，不绑定框架）
├── types/            （共享 TypeScript 类型）
└── utils/            （纯函数，无框架绑定）
```

关键：**共享包要避免框架绑定**，或者为每个框架提供单独的包。

### Q7: 如何限制包之间的依赖？（防止依赖混乱）

**A**: 使用工具强制执行：
```javascript
// 1. ESLint 规则（eslint-plugin-import）
{
  rules: {
    'import/no-restricted-paths': [
      'error',
      {
        zones: [
          // 禁止基础层引用应用层
          {
            target: './packages/utils/src',
            from: './apps/',
            message: 'utils 不能引用 apps 下的代码'
          },
          // 禁止同级非基础包互相引用（根据团队规则）
          {
            target: './packages/ui/src',
            from: './packages/api-client/src',
            message: 'ui 不能直接依赖 api-client，请通过 props/event'
          }
        ]
      }
    ]
  }
}

// 2. pnpm 配置（仅允许特定 workspace 访问）
// .npmrc
only-built-dependencies=true
```

### Q8: Monorepo 中如何进行 Code Splitting？

**A**: 在应用中正常配置即可：
```typescript
// apps/admin-web/vite.config.ts
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        vue: ['vue', 'vue-router', 'pinia'],
        element: ['element-plus'],
        company: ['@company/ui', '@company/api-client', '@company/utils']
      }
    }
  }
}
```

**注意**：应用打包时，workspace 依赖 (`@company/ui` 等) 默认会打入应用 bundle，不需要单独发布 npm 包。

---

## 参考资料

- [pnpm Workspace 文档](https://pnpm.io/workspaces)
- [Turborepo 文档](https://turbo.build/repo/docs)
- [Nx 文档](https://nx.dev/getting-started/intro)
- [Lerna 文档](https://lerna.js.org/)
- [Changesets 文档](https://github.com/changesets/changesets)
- [Microsoft Rush](https://rushjs.io/)
- [Google Bazel](https://bazel.build/)
- [Monorepo.tools](https://monorepo.tools/)（Monorepo 方案对比站）

---

> **文档说明**：本文档全面介绍了 Monorepo 架构的核心概念、优势与挑战、常见实现方案对比、项目结构设计原则、依赖管理策略、构建部署流程以及最佳实践。重点推荐 **pnpm Workspace + Turborepo + Changesets** 的社区主流方案，并提供了从零搭建的完整配置示例（包括 TypeScript、Vue、Vite、ESLint、Prettier 等工具链集成），可直接作为团队 Monorepo 架构落地的实施指南。