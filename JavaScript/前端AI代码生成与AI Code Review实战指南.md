# 前端 AI 代码生成与 AI Code Review 实战指南

> 本文档聚焦 AI 生成代码后的质量闭环：为什么还需要 Review、AI Review 完整流程、分维度 Prompt 模板库、工具链集成（VS Code / Git Pre-commit / CI）、AI 生成代码典型坑点及甄别方法、Vue3+TS 实战走查示例、高频面试题，适合中高级前端工程师团队落地 AI 辅助开发规范。

---

## 目录

- [一、背景：AI 写的代码为什么还要 AI Review？](#一背景ai-写的代码为什么还要-ai-review)
  - [1.1 AI 生成代码的典型问题](#11-ai-生成代码的典型问题)
  - [1.2 AI Review vs 人工 Review 分工](#12-ai-review-vs-人工-review-分工)
  - [1.3 分层防御：质量保障五道关卡](#13-分层防御质量保障五道关卡)
- [二、AI Code Review 完整流程](#二ai-code-review-完整流程)
  - [2.1 六步标准流程](#21-六步标准流程)
  - [2.2 角色与责任划分](#22-角色与责任划分)
  - [2.3 Review 维度总览](#23-review-维度总览)
- [三、分维度 Prompt 模板库](#三分维度-prompt-模板库)
  - [3.1 通用基础 Review 模板](#31-通用基础-review-模板)
  - [3.2 代码规范与风格模板](#32-代码规范与风格模板)
  - [3.3 安全性 Review 模板](#33-安全性-review-模板)
  - [3.4 性能与内存模板](#34-性能与内存模板)
  - [3.5 TypeScript 类型审查模板](#35-typescript-类型审查模板)
  - [3.6 Vue / React 框架最佳实践模板](#36-vue--react-框架最佳实践模板)
  - [3.7 可测试性与边界用例模板](#37-可测试性与边界用例模板)
  - [3.8 可维护性与重构建议模板](#38-可维护性与重构建议模板)
- [四、工具链集成](#四工具链集成)
  - [4.1 VS Code 一键 Review 配置](#41-vs-code-一键-review-配置)
  - [4.2 Git Pre-commit 钩子](#42-git-pre-commit-钩子)
  - [4.3 GitHub PR 自动 Review（Actions）](#43-github-pr-自动-reviewactions)
  - [4.4 静态工具链 + AI 协作](#44-静态工具链--ai-协作)
- [五、AI 生成代码典型坑点与甄别](#五ai-生成代码典型坑点与甄别)
  - [5.1 十大典型坑点清单](#51-十大典型坑点清单)
  - [5.2 安全类坑点识别](#52-安全类坑点识别)
  - [5.3 性能类坑点识别](#53-性能类坑点识别)
  - [5.4 业务逻辑类坑点识别](#54-业务逻辑类坑点识别)
- [六、实战：Vue3 + TS 完整走查示例](#六实战vue3--ts-完整走查示例)
  - [6.1 AI 生成的原始代码](#61-ai-生成的原始代码)
  - [6.2 第一轮：通用规范 Review](#62-第一轮通用规范-review)
  - [6.3 第二轮：安全与性能 Review](#63-第二轮安全与性能-review)
  - [6.4 第三轮：Vue 框架与 TS 类型 Review](#64-第三轮vue-框架与-ts-类型-review)
  - [6.5 第四轮：综合重构建议](#65-第四轮综合重构建议)
  - [6.6 最终优化后的代码](#66-最终优化后的代码)
- [七、面试高频题](#七面试高频题)
- [八、团队落地 Checklist](#八团队落地-checklist)

---

# 一、背景：AI 写的代码为什么还要 AI Review？

## 1.1 AI 生成代码的典型问题

```
AI 不是写"代码"，而是"预测下一个 token"。它对代码的"正确性"没有真正理解。

  典型问题统计（基于某团队 300+ 段 AI 代码 Review 结果）：

  ① 幻觉 API / 废弃 API               35%
     → 调用不存在的 props、用已经废弃的写法

  ② 边界条件缺失                       30%
     → 空值、数组为空、接口失败、loading 态没处理

  ③ 安全性漏洞                         15%
     → XSS（v-html / innerHTML / eval）、SQL 注入、权限缺失

  ④ 性能陷阱                           10%
     → v-for 无 key、computed 里改 ref、onMounted 里重复注册

  ⑤ 类型错误（TS 隐式 any）             8%
     → 大面积 any、泛型缺失、类型断言滥用

  ⑥ 可维护性问题                        2%
     → 魔法数字、无注释、命名不清、单函数过长

  ⚠️ 结论：AI 写的代码"看起来很像正确的代码"，60%~80% 跑起来没问题，
     但剩下的 20% 埋的是生产事故。直接合 main = 埋雷。
```

## 1.2 AI Review vs 人工 Review 分工

```
┌──────────────────────────────────────────────────────────────────┐
│                   AI 能做的（自动化，快，准）                       │
├──────────────────────────────────────────────────────────────────┤
│  ✅ 规范类：命名、格式、长度、函数拆分                               │
│  ✅ 一致性：是否符合团队规范 / ESLint 规则                          │
│  ✅ 安全模式匹配：eval / v-html / innerHTML / dangerouslySetInnerHTML │
│  ✅ 性能反模式：computed 副作用、watch 循环、无 key 的 v-for        │
│  ✅ 类型扫描：any、非空断言 !、类型断言 as 滥用                      │
│  ✅ 边界缺失：没判断 null / 空数组 / 接口错误                       │
│  ✅ 依赖/导入检查：没用到的 import、循环 import                     │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                  必须人工做的（AI 理解力不够）                      │
├──────────────────────────────────────────────────────────────────┤
│  ⭐ 业务逻辑正确性：是否符合产品需求 / 有没有理解错业务              │
│  ⭐ 架构/设计模式选择：抽象是否合理、是否与现有工程模式一致          │
│  ⭐ 复杂边界与异常场景：并发、竞态、极端流量下行为                │
│  ⭐ 用户体验细节：loading 时机、错误提示文案、无障碍 a11y         │
│  ⭐ 团队约定：是否应该用某个库、是否应该复用某个已有的工具函数      │
└──────────────────────────────────────────────────────────────────┘
```

## 1.3 分层防御：质量保障五道关卡

```
AI 生成代码
    │
    ▼
  ① AI 自检（生成时顺便问"你自己 Review 一下这段代码有什么问题？"）
    │  约能发现 40% 问题
    ▼
  ② 静态工具链（ESLint / Prettier / TypeScript / Stylelint）
    │  约能再发现 30% 问题（类型、语法、规范）
    ▼
  ③ AI Code Review（分维度 Prompt 走查）
    │  约能再发现 20% 问题（安全、性能、边界、Vue 反模式）
    ▼
  ④ 人工 Review（高级工程师）
    │  抓业务逻辑与架构问题（约 8%）
    ▼
  ⑤ 灰度 + 监控 + E2E
    抓最后 2% 的极端场景
```

---

# 二、AI Code Review 完整流程

## 2.1 六步标准流程

```
Step 1：生成后第一时间自检
─────────────────────────
  让生成代码的那个 AI 自己 Review 一遍：
  "基于你刚写的这段代码，先自我审查一遍，列出可能的 Bug、
   性能问题、安全漏洞、边界条件缺失，以及如何修改。"

Step 2：静态检查先跑一遍
──────────────────────────
  pnpm type-check  →  TS 类型不过关的直接回炉
  pnpm lint        →  ESLint 报错的让 AI 修
  pnpm build       →  编译不过的不用谈 Review
  ❌ 任何一项不通过 → 不进入 Review 流程

Step 3：分维度 AI 走查
──────────────────────────
  依次过 8 个维度的 Prompt 模板（见第三章）：
  规范 → 安全 → 性能 → 类型 → 框架最佳实践 → 边界 → 可测试性 → 可维护性
  每轮发现问题就改，改完回到 Step 2

Step 4：人工复核
──────────────────────────
  高级工程师/技术负责人：
  • 先看 AI Review 的问题列表是否全部修复
  • 重点看业务逻辑正确性
  • 与现有代码风格/模式是否一致

Step 5：单元测试 + E2E 覆盖
──────────────────────────
  让 AI 根据 Review 出的边界条件写 UT
  覆盖：正常路径 / 空值 / 异常 / 边界
  覆盖率目标 ≥ 80%

Step 6：合并后观察
──────────────────────────
  合入 feature 分支 → 预发环境回归
  → 灰度 10% 流量 → 观察 Sentry/监控 48h
  → 全量
```

## 2.2 角色与责任划分

| 角色 | 负责内容 | 输出物 |
|------|----------|--------|
| **生成代码的 AI** | 产出 V1 代码 + 自检报告 | 代码 + 自检清单 |
| **Review AI（另一个模型/新会话）** | 8 维度走查 + 问题清单 + 修改建议 | Review 报告 |
| **开发者（人）** | 理解问题、修复、权衡取舍 | 修复后的 V2/V3 代码 |
| **Reviewer（人，高级）** | 业务逻辑、架构、与项目一致性 | CR 意见（+ Appr/Req changes） |
| **QA / E2E** | 功能验证、场景覆盖、兼容性 | 测试报告 |

> **关键原则**：用"两个不同的 AI 会话"做生成和 Review。同一个会话的 AI 倾向于"自己不否定自己"，Review 效果大打折扣。最好用不同的模型（生成用 GPT-4o / Claude，Review 用另一个）。

## 2.3 Review 维度总览

```
Review 八大维度（80/20 重点标记 ⭐）：

  ⭐ 1. 安全性（XSS / 注入 / 权限 / 敏感信息）       → 一票否决项
  ⭐ 2. 业务逻辑正确性（边界 / 异常 / 竞态）         → 核心
  ⭐ 3. 性能（内存泄漏 / 重复计算 / 大数据渲染）     → 用户体验
  ⭐ 4. TS 类型质量（any / 泛型 / 断言）            → 长期维护
  ⭐ 5. 框架最佳实践（Vue/React 反模式）            → 框架坑
     6. 代码规范与风格（命名 / 结构 / 复杂度）       → 维护成本
     7. 可测试性（是否好写 UT / 是否有副作用）      → 质量保障
     8. 可维护性（抽象是否合理 / 是否可复用）       → 技术债
```

---

# 三、分维度 Prompt 模板库

> 使用原则：每个模板都是一条独立 Prompt。**每次只给一段代码 + 一个维度的 Prompt**，不要把 8 个维度一次性丢给 AI（注意力分散，效果差）。代码用三反引号包裹，注明"以下是待 Review 的代码："。

## 3.1 通用基础 Review 模板

```text
# 角色
你是一名资深前端 Code Reviewer，审查代码质量。请以挑剔的眼光，不要留情面。

# 任务
审查以下前端代码，列出你能发现的所有问题。
按严重程度排序：🔴 严重（必须改） → 🟡 中等（建议改） → 🟢 轻微（可选改）。

# 输出格式
对每个问题，严格按以下格式：
- 【严重度】问题描述
  - 代码位置：引用具体行/片段
  - 风险说明：可能导致什么后果
  - 修改建议：给出具体怎么改（附代码片段）

# 审查范围（以下全部过一遍）
1. 可能的 Bug / 逻辑错误
2. 边界条件缺失（null / 空数组 / 空字符串 / 0 / NaN / undefined）
3. 错误处理缺失（接口失败、Promise reject、try-catch 覆盖）
4. 安全性风险（XSS / eval / 任意属性访问 / 敏感信息）
5. 性能问题（不必要的重渲染 / 大循环 / 重复计算）
6. 可维护性问题（命名不清 / 魔法数字 / 函数过长 / 重复代码）
7. 类型问题（any / 隐式转换 / 类型断言）

以下是待 Review 的代码：
```

## 3.2 代码规范与风格模板

```text
# 角色
你是前端代码规范审查专家，熟悉 ESLint + Prettier + Element Plus + Vue3 生态。

# 项目规范（团队已约定）
- 命名：组件 PascalCase，变量 camelCase，常量 UPPER_SNAKE_CASE，函数 动+名
- 单函数 ≤ 50 行，单文件 ≤ 300 行
- 禁止魔法数字，必须提取常量并注释含义
- 禁止嵌套三元表达式，超过一层用 if/else 或提前 return
- import 排序：三方库 → 内部工具 → 组件 → 样式
- 注释：业务逻辑必须有注释，Why 优先于 What

# 任务
审查以下代码的规范与风格问题，逐条给出修改建议 + 修改后代码。
不只是指出问题，直接给出修正后的版本。

以下是待 Review 的代码：
```

## 3.3 安全性 Review 模板

```text
# 角色
你是前端安全审计专家，精通 OWASP Top 10 的前端攻击面。

# 任务
审计以下代码的安全性。重点检查：

【高风险项，发现就标 🔴 P0】
1. XSS 注入：v-html / innerHTML / dangerouslySetInnerHTML / document.write
   → 是否对内容做了 XSS 过滤？
2. 任意代码执行：eval() / new Function() / setTimeout("string")
3. 敏感信息：console.log 打印密码/token/手机号/身份证、localStorage 存明文敏感数据
4. 权限控制：前端是否判断了用户角色？纯前端判断是否可被绕过？
5. URL/重定向：location.href = userInput 可能导致钓鱼跳转
6. 请求伪造：请求参数是否可被用户篡改导致越权？

【中风险项 🟡 P1】
7. 客户端校验：是否只有前端校验而后端无校验？（标注提醒）
8. CSP 友好：是否用内联 script / on* 事件处理？
9. Referer / Token：CSRF token 是否正确携带？

# 输出
发现任何 P0 问题直接红色警示 + 修复方案。
安全问题必须给出修复代码，不要只说"注意"。

以下是待 Review 的代码：
```

## 3.4 性能与内存模板

```text
# 角色
你是前端性能优化专家，对 Vue3 运行机制、Vite 打包、浏览器渲染原理非常熟悉。

# 任务
从性能和内存角度审查以下代码，检查：

【组件性能】
1. 列表渲染：v-for 是否有正确且稳定的 key？是否用了 index 当 key？
2. computed：是否存在副作用（computed 里修改 ref）？是否能缓存？
3. watch：是否有 watch 循环触发？immediate/deep 是否必要？
4. 事件：是否在模板里用了箭头函数导致每帧重建？
5. v-if vs v-show：频繁切换的是否用了 v-show？
6. 大列表：超过 100 条数据是否考虑虚拟滚动？

【JS 性能】
7. 循环/数组方法：O(n²) 是否能优化？map/filter 链式能否合并？
8. 对象/数组：是否有不必要的深拷贝 JSON.parse(JSON.stringify)?
9. 定时器/监听：组件卸载时 clearTimeout / removeEventListener / 销毁 observer?

【打包体积】
10. import：是否全量引入了大库？（如 import * as lodash）
11. 路由：是否考虑了动态 import 懒加载？

# 输出
对每个问题给出：问题 → 后果 → 优化代码。

以下是待 Review 的代码：
```

## 3.5 TypeScript 类型审查模板

```text
# 角色
你是 TypeScript 类型体操专家，严格的类型安全信徒。

# 原则
any 是原罪。非空断言 ! 需要理由。as 断言要警惕。

# 任务
审查以下代码的 TS 类型质量：

【🔴 P0 类型问题】
1. 出现 any：隐式 any、显式 any、as any。必须给出正确类型替代。
2. 非空断言 !：是否真的不可能为空？如果是，为什么（如已 if 判断）？
3. 类型断言 as：是否能改用类型守卫 / 泛型 / 重载？
4. 函数参数/返回值缺类型：推断的是否正确？是否需要显式声明？

【🟡 P1】
5. 泛型：本可以抽象的函数/组件是否用了泛型？
6. 联合类型/枚举：是否有分散的字符串字面量应改为 enum / as const?
7. 可选链 ?. / 空值合并 ??：是否用 if (x) 判空导致 number 0 / boolean false 被误判？
8. Record / 索引签名：是否用 any 当对象 value 类型？
9. ref/reactive：Vue 的 ref<T>() / reactive<T> 是否给了泛型？

# 输出
把代码里每一个类型问题列出来，给出修正后的类型定义。

以下是待 Review 的代码：
```

## 3.6 Vue / React 框架最佳实践模板

```text
# 角色
你是 Vue3 Composition API 最佳实践专家（如果是 React 改成 React Hooks 专家）。

# 任务
审查以下 Vue3 代码的框架最佳实践。对照 Vue 官方风格指南逐条过：

【🔴 P0】
1. 组件卸载：是否有副作用没清理？（定时器 / addEventListener / 订阅 / 手动 DOM）
   → 用 onBeforeUnmount 清理了吗？
2. reactive 解构：是否直接解构 reactive 丢失了响应式？
3. ref / computed 使用：是否应该用 computed 的地方写成了普通函数 + ref？
4. v-model 双向绑定：是否正确 .value？

【🟡 P1】
5. props 定义：是否完整声明了 type / default / required / validator？
6. emit 定义：是否声明了 emits 类型？是否用了类型声明式 emit？
7. 生命周期：onMounted 里是否放了本应 watch/computed 做的事？
8. provide/inject：是否加了 Symbol key + 类型？
9. 样式：是否加了 scoped？::v-deep 是否必要？
10. Pinia/Vuex：是否把应该放 store 的放组件本地了？

# 输出
逐条列出问题 + 修正代码。

以下是待 Review 的 Vue3 代码：
```

## 3.7 可测试性与边界用例模板

```text
# 角色
你是一个追求覆盖率 100% 的测试工程师。

# 任务
分析以下代码，并输出：

1. 列出这段代码所有可能的输入 / 状态分支（枚举）
2. 针对每个分支，给出边界用例：
   - 正常值用例
   - 空值/零值用例（null / undefined / 0 / '' / [] / {}）
   - 异常值用例（超长字符串 / 负数 / NaN / 非法字符）
   - 并发/竞态用例（如果有异步）
   - 错误路径用例（接口失败/超时/返回空）
3. 判断这段代码是否"可测试"：
   - 是否有难以 mock 的硬依赖？（Date.now / Math.random / DOM）
   - 是否有隐藏的全局状态？
   - 是否把副作用和纯逻辑耦合在一起？
4. 给出一份 vitest 的 UT 骨架代码，覆盖你列出的用例。

以下是待 Review 的代码：
```

## 3.8 可维护性与重构建议模板

```text
# 角色
你是一名资深架构师，负责代码的长期健康度。

# 任务
跳出 Bug 思维，从架构/可维护性角度审查：

1. **职责单一**：这个组件/函数是否做了太多事？能否拆分？
2. **重复代码**：有没有能抽取为 composable / utils / 公共组件的？
3. **命名合理性**：变量/函数名是否能让新同学 3 秒内看懂？需不需要补注释？
4. **魔法数字/字符串**：数字、字面量是否该提取成常量/配置？
5. **过早优化 / 过度设计**：是否用了复杂的抽象，但实际只调用一次？
6. **与现有项目复用**：项目工具库中是否已有等价的函数，但重复造了轮子？
7. **扩展友好**：后续如果加一个字段/一种状态，改动面是否太大？是否需要状态机 / 策略模式？
8. **注释 / 文档**：关键算法/业务规则有没有 Why 级注释？

# 输出
给出：保留 → 重命名 → 抽取 → 拆分 → 复用 的清单，并给出重构后的代码骨架。

以下是待 Review 的代码：
```

---

# 四、工具链集成

## 4.1 VS Code 一键 Review 配置

```jsonc
// .vscode/tasks.json —— 绑定快捷键一键执行 AI Review
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "AI Code Review: 当前文件",
      "type": "shell",
      "command": "npx",
      "args": [
        "ai-review",
        "--file", "${file}",
        "--dimensions", "security,performance,vue,typescript"
      ],
      "presentation": { "reveal": "always", "panel": "dedicated" },
      "problemMatcher": []
    }
  ]
}
```

```jsonc
// .vscode/keybindings.json —— 快捷键绑定（Ctrl+Shift+R 触发）
[
  {
    "key": "ctrl+shift+r",
    "command": "workbench.action.tasks.runTask",
    "args": "AI Code Review: 当前文件"
  }
]
```

```bash
# 方案 A：Cursor / Trae / Windsurf 等 AI IDE —— 选中代码 → 右键 → Ask AI
# 直接粘贴第三章的 Prompt 模板 + 选中代码即可，无需额外工具

# 方案 B：GitHub Copilot Chat（VS Code）
# 在 Chat 里输入：
#   @workspace /explain 规范 + 安全 + 性能审查当前文件，按严重度排序
# （效果略低于手工定制 Prompt，但足够日常用）

# 方案 C：本地 CLI（可选，自建）
# pnpm add -D @ai-sdk/openai zod
# 写一个脚本调用 GPT-4o-mini + 模板库批量跑 PR 变更文件
```

## 4.2 Git Pre-commit 钩子

```bash
# 用 husky + lint-staged 在 commit 前自动跑 AI Review 摘要
# 先安装：
pnpm add -D husky lint-staged
npx husky init
```

```bash
# .husky/pre-commit
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

# 第 1 关：静态检查先过
pnpm exec lint-staged
pnpm exec tsc --noEmit

# 第 2 关：变更文件 AI 安全扫描摘要（5 秒内快扫）
echo "🤖 AI 安全扫描变更文件..."
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(vue|ts|tsx|js)$')
if [ -n "$FILES" ]; then
  # 轻量 AI 安全扫描（本地脚本，不阻塞 commit，只给提示）
  node scripts/ai-security-scan.js "$FILES" || true
fi

echo "✅ Pre-commit 检查通过，建议进入 PR 阶段后做完整 AI Review"
```

```javascript
// scripts/ai-security-scan.js —— 轻量本地规则匹配（不依赖网络）
const fs = require('fs')
const files = process.argv.slice(2)

const DANGER_PATTERNS = [
  { pattern: /\bv-html\s*=/, level: '🔴 P0', msg: 'v-html 可能导致 XSS，请确认已做 HTML 过滤' },
  { pattern: /\.innerHTML\s*=/, level: '🔴 P0', msg: 'innerHTML 可能导致 XSS' },
  { pattern: /\beval\s*\(/, level: '🔴 P0', msg: 'eval() 任意代码执行风险' },
  { pattern: /new Function\s*\(/, level: '🔴 P0', msg: 'new Function() 代码注入风险' },
  { pattern: /:key=["']?\s*index\b/, level: '🟡 P1', msg: 'v-for 用 index 当 key 可能导致渲染错乱' },
  { pattern: /console\.(log|debug)\s*\(/, level: '🟡 P1', msg: '生产代码不应包含 console.log' },
]

let hasIssue = false
for (const file of files) {
  const content = fs.readFileSync(file, 'utf8')
  for (const { pattern, level, msg } of DANGER_PATTERNS) {
    if (pattern.test(content)) {
      console.log(`${level} [${file}] ${msg}`)
      hasIssue = true
    }
  }
}

if (!hasIssue) console.log('✅ 快速规则扫描无高危项')
process.exit(0) // 不阻塞 commit，只做提示
```

## 4.3 GitHub PR 自动 Review（Actions）

```yaml
# .github/workflows/ai-code-review.yml
name: AI Code Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    if: contains(github.event.pull_request.labels.*.name, 'ai-review')  # 打标签才跑
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: 获取 PR Diff
        id: diff
        run: |
          git diff origin/${{ github.base_ref }}...HEAD -- '*.vue' '*.ts' '*.tsx' > pr-diff.txt
          echo "diff_size=$(wc -c < pr-diff.txt)" >> $GITHUB_OUTPUT
          cat pr-diff.txt

      - name: AI Review（调用自托管 API / 第三方服务）
        if: steps.diff.outputs.diff_size > 0
        id: ai
        uses: 你的/ai-review-action@v1  # 如 coderabbit / codiumai / 自建
        with:
          model: gpt-4o-mini
          dimensions: security,performance,vue,typescript,bugs
          diff-file: pr-diff.txt

      - name: 评论到 PR
        uses: thollander/actions-comment-pull-request@v2
        with:
          message: |
            ## 🤖 AI Code Review 报告
            ${{ steps.ai.outputs.report }}

            > 严重度：🔴 P0 必须改 | 🟡 P1 建议改 | 🟢 P2 可选
            > 请在人工 CR 前先修复所有 🔴 项
          comment_tag: ai-review-report
```

> 注：GitHub 已有成熟第三方 AI Review 工具（CodeRabbit / Codeium / Sourcery / GitHub Copilot for PRs），多数开源项目免费，优先用现成的，不用自己造轮子。

## 4.4 静态工具链 + AI 协作

```
推荐顺序（左到右，先静态后 AI）：

  Prettier → ESLint → TypeScript tsc → Stylelint → AI Review
     │          │          │             │           │
     │          │          │             │           └ 业务逻辑/安全/架构/边界
     │          │          │             └────────────── CSS 规范
     │          │          └──────────────────────────── TS 类型严格校验
     │          └─────────────────────────────────────── 代码规范+常见反模式
     └────────────────────────────────────────────────── 纯格式
```

```jsonc
// .eslintrc-auto-merge.cjs —— 配合 AI 用的规则集
// 先把静态工具能抓的都抓了，剩下的再让 AI 做
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended-requiring-type-checking',
    'plugin:vue/vue3-recommended',
    'plugin:security/recommended',           // ← 安全规则（抓 eval/innerHTML/XSS）
    'plugin:sonarjs/recommended',             // ← Sonar 圈复杂度/重复代码
    'plugin:perfectionist/recommended-natural',
  ],
  rules: {
    '@typescript-eslint/no-explicit-any': 'error',        // ← any 红线
    '@typescript-eslint/no-non-null-assertion': 'warn',   // ← ! 警告
    'vue/no-v-html': 'error',                             // ← v-html 禁止
    'security/detect-eval-with-expression': 'error',
    'security/detect-inner-html': 'warn',
    'sonarjs/cognitive-complexity': ['warn', 15],         // ← 函数复杂度
  },
}
```

---

# 五、AI 生成代码典型坑点与甄别

## 5.1 十大典型坑点清单

| # | 坑点 | AI 为什么会犯 | 人工识别方法 |
|---|------|--------------|--------------|
| 1 | **v-html / innerHTML 无过滤** | 训练数据里到处是 innerHTML，AI 学进去了 | grep / ESLint rule `vue/no-v-html` |
| 2 | **v-for 用 index 作 key** | 示例代码里写起来方便，AI 喜欢抄 | 搜索 `:key="index` / `:key="i` |
| 3 | **computed 里有副作用（改 ref）** | 不理解 Vue 响应式执行时机 | 看 computed 回调里是否 `.value =` |
| 4 | **组件卸载不清理副作用** | 训练数据很少写完整示例 | 看 setTimeout/addEventListener/observer 是否有对应清理 |
| 5 | **大面积 any / `as any`** | 为了让代码"看起来能编译"，AI 直接塞 any | TS strict 模式 + ESLint `no-explicit-any` |
| 6 | **接口错误不处理** | 只写 happy path 最短，异常流程描述长 | 看 async 函数有没有 try-catch / .catch() |
| 7 | **loading 状态缺失** | 同上，只写成功态流程 | 看异步操作前后是否改了 loading ref |
| 8 | **空值未判断** | 假设数据一定存在 | 看数组操作前是否判断 length，对象访问前是否判空 |
| 9 | **废弃 API**（如 Vue2 的 `this.$set`） | 训练数据包含大量旧版 API | 查 Vue/React 官方文档迁移指南 |
| 10 | **eval / new Function()** | 老代码常见写法 | 搜索关键字 |

## 5.2 安全类坑点识别

```
【高风险关键词 - 代码里出现必须停下审查】

  XSS 类：
    v-html              → 默认不信任，除非内容走了 DOMPurify.sanitize()
    innerHTML           → 同上
    dangerouslySetInnerHTML → React 版本同上
    document.write      → 几乎总是有问题
    location.href = xxx → 如果 xxx 含用户输入，可能钓鱼跳转

  代码执行类：
    eval(xxx)           → 基本禁用，99% 场景有替代方案
    new Function(code)  → 同上
    setTimeout(str, n)  → 传字符串会被 eval，应传函数引用

  信息泄露类：
    console.log(token/password/userInfo) → 生产 console.* 要么移除要么拦截
    localStorage.setItem('token', xxx)   → token 应放 cookie httponly
    文件里硬编码 API Key / Secret        → 应读取环境变量

  权限类：
    前端 if (user.role === 'admin') 才显示按钮
    → 按钮可以隐藏，但后端接口必须再鉴权（AI 常漏掉这点）
```

## 5.3 性能类坑点识别

```
【Vue/React 性能反模式 - 一眼识别】

  1. v-for 用 index 作 key
     <div v-for="(item, index) in list" :key="index"> ← 坑！
     后果：增删中间项时复用错误的 DOM，输入框值错乱
     改：用 item.id / item.uuid 这种业务唯一值

  2. computed 里修改 ref / 调接口
     const bad = computed(() => { count.value++; return data.value.length })
     后果：computed 依赖变化 → 重新算 → 改 ref → 依赖变 → 死循环

  3. watch deep 监听大对象但没做具体字段区分
     watch(() => bigObj, () => { ... }, { deep: true })
     后果：bigObj 里任何一个小字段变更都触发整段逻辑

  4. onMounted 注册事件但 onBeforeUnmount 不解绑
     → 内存泄漏，组件反复挂载后监听器越来越多

  5. 模板里写 @click="() => doSth(x)"
     → 每次渲染都创建新函数引用 → 子组件 Props 变化 → 多余重渲染
     （小列表无所谓，大表格 / 高频刷新才是坑）
```

## 5.4 业务逻辑类坑点识别

```
AI 最不擅长的是"业务语义理解"，需要人工重点审：

  1. "时间"相关
     - 前后端时区是否一致？（UTC vs Asia/Shanghai）
     - 开始时间 ≤ 结束时间？
     - 是否允许跨越天/月/年边界？

  2. "金额/数量"相关
     - 浮点数精度：0.1 + 0.2 ≠ 0.3（JS 原生坑，AI 很可能忽视）
     - 是否保留 2 位小数？
     - 是否有上限/下限校验？

  3. "状态流转"相关
     - 订单：PENDING → PAID → CANCELLED 能跳吗？
     - AI 可能写了 if(status==='xxx') 但没阻止非法跳转
     - 需要画状态机确认

  4. "重复提交/并发"相关
     - 点提交按钮 2 次会怎样？
     - 快速切 Tab 是否会有竞态？
     - 接口慢时反复点击会怎样？
     → 需要幂等保护，AI 通常不主动加（除非你在 prompt 里明确要求）
```

---

# 六、实战：Vue3 + TS 完整走查示例

> 我们模拟一次真实流程：AI 先生成一个"用户搜索分页列表"组件 → 分 4 轮 Review → 最终优化版。

## 6.1 AI 生成的原始代码

```vue
<!-- 原始版本：AI 第一次生成 -->
<template>
  <div class="user-list">
    <input v-model="keyword" placeholder="搜索">
    <button @click="search">搜索</button>

    <ul>
      <li v-for="(user, index) in users" :key="index" v-html="user.name"></li>
    </ul>

    <button @click="page--">上一页</button>
    <span>{{ page }}</span>
    <button @click="page++">下一页</button>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, onMounted } from 'vue'

const keyword = ref('')
const users = ref([])
const page = ref(1)

async function search() {
  const res = axios.get('/api/users', { params: { q: keyword.value, page: page.value } })
  users.value = res.data.data.list
}

onMounted(() => {
  search()
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') search()
  })
})
</script>

<style>
.user-list { color: red }
</style>
```

## 6.2 第一轮：通用规范 Review

```text
审查结果（模板 3.2 + 3.1）：

🔴 P0 - 1. 异步函数 search() 缺少 await
   代码：const res = axios.get(...)
   风险：res 是 Promise，不是响应数据，users.value 赋值给了 Promise，渲染崩
   修改：加 await → const res = await axios.get(...)

🔴 P0 - 2. 缺少 try-catch / 错误处理
   代码：axios.get 无异常捕获
   风险：接口 5xx / 4xx → 未捕获 Promise reject → 控制台报错，用户无提示
   修改：try-catch 包裹，错误时 ElMessage.error()

🟡 P1 - 3. page 变量缺少边界：上一页可点到 0 / 负数
   风险：分页异常
   修改：page-- 时 if(page.value > 1) page.value--
        下一页也要判断总数 pageSize

🟡 P1 - 4. 样式缺 scoped
   风险：.user-list 的 color:red 污染全局
   修改：<style scoped>

🟡 P1 - 5. 命名：search() 太泛，应为 searchUsers 或 fetchUsers
```

## 6.3 第二轮：安全与性能 Review

```text
审查结果（模板 3.3 + 3.4）：

🔴 P0 - 1. v-html 直接输出 user.name → XSS 漏洞
   风险：若 user.name = "<img src=x onerror=alert(1)>" → 注入任意脚本
   修改：
     a. 若不需要富文本 → 直接 {{ user.name }} 文本插值
     b. 若需要富文本 → 通过 DOMPurify.sanitize(user.name) 过滤

🔴 P0 - 2. keydown 监听器未在卸载时移除
   风险：组件多次挂载后监听器叠加，按一次 Enter 触发 N 次 search
   修改：onBeforeUnmount 里 removeEventListener，或直接在 input 上加 @keyup.enter

🟡 P1 - 3. v-for 用 index 作 key
   风险：分页切换时列表项错位 / 输入状态错位
   修改：:key="user.id"（假设 user 有 id 字段）

🟡 P1 - 4. 输入框搜索缺少防抖
   风险：快速输入时每个字符都触发请求
   修改：搜索按钮+回车触发是对的，但如果要做实时搜索要加 useDebounce

🟡 P1 - 5. 无 loading 状态
   风险：接口慢时用户感知不到，容易重复点击
   修改：加 loading ref，请求期间按钮 loading + 禁用
```

## 6.4 第三轮：Vue 框架与 TS 类型 Review

```text
审查结果（模板 3.5 + 3.6）：

🔴 P0 - 1. 全程 any：users = ref([]) 未指定类型
   风险：后续 user.xxx 属性访问 TS 不校验，写错字段不报错
   修改：
     interface User { id: number; name: string; email: string; /* ... */ }
     const users = ref<User[]>([])

🟡 P1 - 2. keyword / page 也应加类型
   const keyword = ref<string>('')
   const page = ref<number>(1)

🟡 P1 - 3. axios 响应未给泛型
   应该：
     interface ApiResponse<T> { code: number; data: T; message: string }
     const res = await axios.get<ApiResponse<{ list: User[]; total: number }>>(...)

🟡 P1 - 4. 建议抽取为 composable
   分页 + 搜索逻辑可复用，建议：usePagination + useUserSearch，而不是全堆组件里

🟡 P1 - 5. input 建议用 v-model.trim
```

## 6.5 第四轮：综合重构建议

```text
审查结果（模板 3.7 + 3.8）：

🟡 P1 - 1. 边界测试需要覆盖：
   • keyword = '' 空搜索（返回全部？）
   • 接口返回 null / 空数组
   • 接口 401 / 500 / 网络超时
   • 第一页点"上一页"、最后一页点"下一页"
   • 快速连点"下一页" 5 次是否只发最后一次请求？（应加请求锁）

🟡 P1 - 2. 建议增加请求锁，避免并发多次请求：
   const loading = ref(false)
   if (loading.value) return; loading.value = true → finally loading.value = false

🟡 P1 - 3. 总页数需要从接口拿 total 计算，目前只靠 page 自增自减不够

🟡 P1 - 4. 空状态：无数据时展示"暂无数据"，不要空白页面
```

## 6.6 最终优化后的代码

```vue
<!-- 最终版：4 轮 Review + 修复后 -->
<template>
  <div class="user-list">
    <el-input
      v-model.trim="keyword"
      placeholder="请输入用户名搜索"
      clearable
      :disabled="loading"
      @keyup.enter="handleSearch"
    >
      <template #append>
        <el-button :loading="loading" type="primary" @click="handleSearch">
          搜索
        </el-button>
      </template>
    </el-input>

    <el-table
      v-loading="loading"
      :data="users"
      stripe
      style="margin-top: 16px"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="用户名" show-overflow-tooltip />
      <el-table-column prop="email" label="邮箱" show-overflow-tooltip />
    </el-table>

    <el-empty v-if="!loading && users.length === 0" description="暂无用户数据" />

    <el-pagination
      style="margin-top: 16px; justify-content: flex-end"
      background
      layout="prev, pager, next, total"
      :total="total"
      :page-size="PAGE_SIZE"
      v-model:current-page="page"
      :disabled="loading"
      @current-change="handlePageChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// ============ 类型定义 ============
interface User {
  id: number
  name: string
  email: string
}

interface ApiResponse<T> {
  code: number
  data: T
  message?: string
}

interface UserListResponse {
  list: User[]
  total: number
}

// ============ 常量 ============
const PAGE_SIZE = 20

// ============ 响应式状态（带泛型） ============
const keyword = ref<string>('')
const users = ref<User[]>([])
const total = ref<number>(0)
const page = ref<number>(1)
const loading = ref<boolean>(false)

// 请求锁：防止多次点击/并发请求
const isRequesting = computed(() => loading.value)

// ============ 业务方法 ============
async function fetchUsers() {
  if (isRequesting.value) return
  loading.value = true
  try {
    const { data } = await axios.get<ApiResponse<UserListResponse>>('/api/users', {
      params: { q: keyword.value, page: page.value, pageSize: PAGE_SIZE },
    })
    if (data.code === 200) {
      users.value = data.data.list
      total.value = data.data.total
    } else {
      ElMessage.error(data.message || '获取用户列表失败')
    }
  } catch (err) {
    ElMessage.error('网络错误，请稍后重试')
    console.error('[UserList] fetch users failed:', err)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  // 搜索时回到第 1 页
  if (page.value !== 1) {
    page.value = 1
  } else {
    fetchUsers()
  }
}

function handlePageChange(newPage: number) {
  // 分页变化已在 page v-model 中更新
  fetchUsers()
}

// page 变化时自动刷新（搜索时手动改 page 会触发）
// 用 watch 而不是在 handleSearch 里两次调
watch(page, fetchUsers)

onMounted(fetchUsers)
// ⭐ 无需手动 addEventListener，@keyup.enter 已处理
// 也不需要 removeEventListener
</script>

<style scoped lang="scss">
.user-list {
  padding: 16px;
  :deep(.el-table) {
    border-radius: 8px;
  }
}
</style>
```

---

# 七、面试高频题

**Q1：AI 生成的代码可以直接合 main 吗？为什么？**

> 不能。AI 生成的是"看起来像正确的代码"，存在 6 类高频问题：幻觉 API、边界缺失、XSS 等安全漏洞、性能反模式、TS any、业务逻辑错误。合入前至少要经过：静态工具链（type-check/lint/build）+ AI 分维度 Review（8 大维度）+ 人工业务逻辑复核 + UT 覆盖。直接合就是在生产埋雷。

**Q2：AI Code Review 和人工 Review 怎么分工？哪些必须人工？**

> 分工：AI 做"模式匹配"类工作——规范、安全漏洞关键词、Vue/React 反模式、TS 类型缺失、性能反模式、边界缺失枚举。这些 AI 速度快、覆盖全、不会漏。人工做"理解力"类工作——业务逻辑对不对、抽象是否合理、是否符合项目既有模式、复杂并发/竞态场景。**必须人工的**：产品需求匹配度、架构设计、团队约定、用户体验细节。

**Q3：如何最大化 AI Review 效果？有什么技巧？**

> 4 个技巧：① **会话/模型分离**：生成代码和 Review 用不同的 AI 会话（最好不同模型），同会话的 AI 会袒护自己。② **分维度给 Prompt**：不要一次问"帮我 Review 全部"，而是按安全、性能、类型、Vue 最佳实践分次过，每次一个维度。③ **给上下文**：Review 前把项目的 ESLint 配置、框架版本、团队规范贴给 AI，不然 AI 用的是互联网平均水平。④ **输出结构化**：强制要求按严重度分级（🔴 P0 / 🟡 P1 / 🟢 P2）+ 问题→风险→修改代码三段式，不然输出太散。

**Q4：AI 生成的代码有 XSS 风险，怎么一眼识别？**

> 搜关键字：`v-html` / `innerHTML` / `dangerouslySetInnerHTML` / `eval` / `new Function` / `document.write`，出现这些一定停下来人工审查。最佳实践是在 ESLint 里开 `vue/no-v-html` 和 `security/detect-eval-with-expression` 规则，CI 就卡死，不要靠 AI Review 这层才发现。

**Q5：Review 时发现 AI 生成代码大面积用 `any` 怎么办？**

> 这是 AI 为了"让代码看起来能编译"偷懒的做法。**必须全部改掉**，不能留。处理手段：① 开启 TS `strict: true` + ESLint `@typescript-eslint/no-explicit-any: error`，直接编译不过。② 在生成代码的 Prompt 里明确加"严格 TS，不允许 any，所有 ref/reactive 给泛型，所有函数给参数和返回值类型"。③ 如果实在不确定类型，用 `unknown` 代替 `any`，迫使用户加类型守卫。

**Q6：PR 里让 AI 自动 Review 有什么推荐工具？**

> 开源/免费：① **GitHub Copilot for Pull Requests**（官方，和 PR 集成深）② **CodeRabbit**（分维度评论、增量 Review、给修复建议）③ **Sourcery**（Python/JS 都支持，重构建议强）④ **CodiumAI PR-Agent**（开源可自建，支持 GPT-4o / Claude）⑤ 自建：GitHub Actions + 模型 API + 第三章的 Prompt 模板（适合对数据敏感不能出公司的场景）。小团队直接用 CodeRabbit 或 Copilot for PRs 即可，不用自己搭。

---

# 八、团队落地 Checklist

```
团队约定：
  □ 明确禁止"AI 生成代码直接合 main"，必须走 Review 流程
  □ 约定生成和 Review 用不同模型/会话，禁止同会话自审
  □ 规定 Review 前必须通过 type-check + lint + build
  □ 8 维度 AI Review 模板库进团队 Wiki，新人统一学习
  □ 约定严重度分级标准：🔴 P0 必须改 / 🟡 P1 建议改 / 🟢 P2 可选

静态工具链：
  □ TS strict: true 全开（严格模式）
  □ ESLint 规则包含 no-explicit-any / vue/no-v-html / security 规则集
  □ Husky + lint-staged commit 前跑静态检查
  □ CI 用 npm ci / frozen-lockfile + 完整 type-check / lint / build / test

AI Review 落地：
  □ VS Code 团队级 snippet 存放 8 个 Prompt 模板
  □ PR 自动 AI Review（CodeRabbit / Copilot for PRs / 自建）
  □ 所有 P0 安全问题必须在人工 CR 前修复
  □ 代码生成的 Prompt 模板强制包含：严格 TS / 错误处理 / loading / scoped / 不用 index 作 key

人工 Review 兜底：
  □ 人工 CR 必须重点看业务逻辑正确性
  □ 人工 CR 必须检查与现有代码风格/抽象一致性
  □ AI Review 报告里的所有 P0/P1 项必须有修复或"不修复理由"记录
  □ 合并前确认有对应的 UT / E2E 覆盖边界情况

持续改进：
  □ 每月回顾一次"AI 生成 → AI Review 漏过的线上 Bug"
  □ 把漏过的问题沉淀进 Prompt 模板库
  □ 更新团队 ESLint / TS 规则，把能静态卡的都卡掉
```
