- [npm与pnpm安装机制对比](#npm与pnpm安装机制对比)
  - [‌核心技术差异](#核心技术差异)
  - [性能对比](#性能对比)
  - [‌安全性与工程化特性](#安全性与工程化特性)
- [npm install --legacy-peer-deps](#npm-install---legacy-peer-deps)
      - [作用和原理](#作用和原理)
      - [工作流程详解](#工作流程详解)
- [npm install --force](#npm-install---force)
      - [作用](#作用)
      - [具体行为](#具体行为)
      - [工作流程详解](#工作流程详解-1)

### npm与pnpm安装机制对比 

pnpm与npm的核心区别体现在依赖存储机制、安装效率和安全性三个维度，其核心区别为：‌**pnpm采用硬链接共享全局存储的依赖项，npm采用层级依赖树与扁平化结构‌。**

#### ‌核心技术差异

**1.‌依赖存储机制‌。**
 - npm：通过层级依赖树安装依赖，采用扁平化结构处理重复依赖。相同版本的依赖可能被提升到根目录，导致"幻影依赖"（未声明的依赖被错误引用，即每个项目的依赖独立存储于 node_modules，即使多个项目使用相同版本的包，也会重复下载和存储。例如，10 个项目安装 react 会产生 10 份副本，占用大量磁盘空间
    **问题：依赖冗余导致磁盘浪费，尤其在 Monorepo 或多项目环境中更为显著**

 - pnpm：使用硬链接将依赖链接到全局存储库（.pnpm-store），确保同一版本的依赖仅存储一次。项目目录通过符号链接引用依赖，避免冗余，例如，10 个项目安装 react 仅需一份文件。
    **优势：节省磁盘空间高达 80% 以上，适合大型项目或开发机多项目场景。**

 **2.安装逻辑。**
 - npm：逐层解析依赖树，从 npm3 开始使用 扁平化依赖结构，将子依赖提升到顶层 node_modules。例如，包 A 依赖 lodash@1.0 和包 B 依赖 lodash@2.0 可能共存于顶层，导致“幽灵依赖”（未声明但可访问的包）和版本冲突风险。
 - pnpm：基于内容寻址存储机制，优先复用全局缓存。首次安装完成后的后续安装速度提升2-3倍，并且通过 符号链接模拟扁平化结构，但实际依赖层级严格遵循声明关系。每个包仅能访问自身声明的依赖，避免版本冲突和幽灵依赖问题。 示例：若包 A 和 B 依赖不同版本的 lodash，pnpm 会分别存储并在各自作用域内引用，确保隔离性。

#### 性能对比

**1.‌磁盘空间占用‌。**
- pnpm通过共享依赖节省40%-70%空间。例如10GB的node_modules用pnpm可能仅占3GB
- npm的扁平化结构导致重复存储，多个项目会累积大量冗余文件

**2.安装速度‌**
- 测显示pnpm在大型项目中比npm快2倍以上，特别是在CI/CD环境或弱网条件下优势显著

#### ‌安全性与工程化特性
**1.‌依赖安全‌。**
- pnpm默认启用strict-peer-dependencies，安装阶段即校验版本冲突，避免错误依赖渗透
- npm的扁平化结构可能导致未声明的依赖被意外引用，引发构建环境不一致问题


### npm install --legacy-peer-deps

这个选项通常用于解决npm v7+版本中引入的peer dependencies自动安装问题。在npm v7之前（v6及以下），当安装一个包时，如果它的peer dependencies没有被满足，npm只会给出警告，但仍然会继续安装。

 从npm v7开始，npm会在遇到**peer dependencies（对等依赖）** 冲突时自动安装依赖，并且如果无法自动解决冲突，则会报错并终止安装。

 ###### 作用和原理

 **1.peer dependencies 是什么？**

 当一个包（Package A）声明另一个包（Package B）为 peerDependency 时，它意味着：
 “我需要 Package B，但不会自动安装它。请确保宿主项目已经安装了 Package B，且版本符合我的要求。”
 常见场景：React 组件库会声明 react 和 react-dom 为对等依赖。

 **2.npm v7+ 的默认行为变化**
    npm v7 开始自动安装 peer dependencies（之前版本只警告不自动安装）。
    如果项目中安装的 peer dependency 版本不满足要求，npm 会报错并终止安装。
 **3.--legacy-peer-deps 的作用**
    使用此标志会回退到 npm v6 的行为：
- 忽略 peer dependencies 的版本冲突警告。
- 跳过自动安装 peer dependencies。
- 继续安装其他依赖（即使 peer dependency 不满足要求）。

**将此命令作为临时手段，同时尽快修复根本的依赖冲突，确保项目稳定性。**

###### 工作流程详解
  ```mermaid
graph TB
    A[开始 npm install --legacy-peer-deps] --> B[解析 package.json 依赖树]
    B --> C{检查 peerDependencies}
    C -->|普通安装流程| D[验证 peerDeps 版本兼容性]
    C -->|--legacy-peer-deps 模式| E[跳过 peerDeps 版本检查]
    E --> F[忽略自动安装 peerDeps]
    F --> G[仅安装直接依赖]
    G --> H{是否存在 peerDeps 冲突？}
    H -->|是| I[打印警告但不中断安装]
    H -->|否| J[正常写入 node_modules]
    I --> J
    J --> K[生成/更新 package-lock.json]
    K --> L[安装完成]
```

### npm install --force

###### 作用
`--force` 会强制 npm 去获取远程资源，即使本地已经存在该资源（比如之前安装过，但可能损坏或不完整）。同时，它也会忽略某些缓存或校验问题，并重新下载安装包。

######  具体行为
-  1. 忽略缓存：通常npm会从本地缓存安装包以加快速度，但使用`--force`会跳过缓存，重新下载。
-  2. 覆盖本地已存在的版本：如果本地node_modules中已经安装了某个包，但你想强制重新安装，这个命令可以做到。
- 3. 它也会继续执行peer dependency的自动安装（与`--legacy-peer-deps`不同，后者是绕过peer dependency的检查）。
###### 工作流程详解
  ```mermaid
graph LR;
A[开始安装] --> B{检查缓存}
B -->|缓存校验失败| C[重新下载包]
B -->|缓存正常| D[使用缓存]
C --> E[覆盖 node_modules]
D --> E
E --> F[写入 package-lock.json]
```
**与 --legacy-peer-deps 的区别**

 | 特性       | `--force`          | `--legacy-peer-deps`               |
|:----------|:------------:|------------------:|
| 主要目标      | 解决缓存/版本锁定问题  | 绕过 peerDependencies 冲突      |
| 覆盖范围      | 所有依赖 | 仅 peerDependencies |
| 是否重新下载    | 强制重新下载所有包 | 仅改变依赖解析逻辑         |
| 典型使用场景    | 包损坏、校验失败、锁定文件不一致 | React/Angular 等生态版本冲突|