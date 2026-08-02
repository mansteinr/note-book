# Vue3 key 属性深度解析

> 本文档系统介绍 Vue3 中 `key` 属性的概念、作用机制、使用场景、最佳实践及注意事项。涵盖 key 的定义与核心功能、列表渲染中的 diff 算法优化、不同类型 key 值的对比、常见使用误区、特殊场景应用策略（动画过渡、组件状态保持等），并配代码示例说明。

---

## 目录

- [一、key 属性概述](#一key-属性概述)
  - [1.1 什么是 key](#11-什么是-key)
  - [1.2 key 的核心功能](#12-key-的核心功能)
  - [1.3 key 的基本用法](#13-key-的基本用法)
- [二、key 与 diff 算法](#二key-与-diff-算法)
  - [2.1 虚拟 DOM 与 diff](#21-虚拟-dom-与-diff)
  - [2.2 同层比较原则](#22-同层比较原则)
  - [2.3 key 在 diff 中的作用](#23-key-在-diff-中的作用)
  - [2.4 有 key vs 无 key 的 diff 流程](#24-有-key-vs-无-key-的-diff-流程)
- [三、key 工作原理详解](#三key-工作原理详解)
  - [3.1 patchKeyedChildren 算法](#31-patchkeyedchildren-算法)
  - [3.2 五步 diff 流程](#32-五步-diff-流程)
  - [3.3 复用与重建的本质](#33-复用与重建的本质)
- [四、key 值类型对比](#四key-值类型对比)
  - [4.1 字符串 key](#41-字符串-key)
  - [4.2 数字 key](#42-数字-key)
  - [4.3 Symbol key](#43-symbol-key)
  - [4.4 类型选择建议](#44-类型选择建议)
- [五、常见使用误区](#五常见使用误区)
  - [5.1 用 index 作为 key](#51-用-index-作为-key)
  - [5.2 用随机数作为 key](#52-用随机数作为-key)
  - [5.3 用对象引用作为 key](#53-用对象引用作为-key)
  - [5.4 key 不唯一](#54-key-不唯一)
  - [5.5 动态修改 key](#55-动态修改-key)
- [六、特殊场景应用](#六特殊场景应用)
  - [6.1 动画过渡](#61-动画过渡)
  - [6.2 组件状态保持](#62-组件状态保持)
  - [6.3 强制重新渲染](#63-强制重新渲染)
  - [6.4 表单输入重置](#64-表单输入重置)
  - [6.5 keep-alive 缓存](#65-keep-alive-缓存)
- [七、最佳实践](#七最佳实践)
  - [7.1 key 选择原则](#71-key-选择原则)
  - [7.2 代码规范](#72-代码规范)
  - [7.3 性能优化](#73-性能优化)
- [八、FAQ](#八faq)
- [附录 源码索引](#附录-源码索引)

---

## 一、key 属性概述

### 1.1 什么是 key

`key` 是 Vue 中一个特殊的 attribute，用于标识虚拟 DOM 节点的唯一性。它主要在 Vue 的虚拟 DOM diff 算法中发挥作用，帮助 Vue 识别节点，从而高效地复用和重新排序现有元素。

```vue
<template>
  <!-- key 用于列表渲染 -->
  <div v-for="item in list" :key="item.id">
    {{ item.name }}
  </div>
</template>
```

**key 的本质**：
- 它是虚拟 DOM 节点的"身份证号"
- Vue 通过 key 判断新旧节点是否是"同一个节点"
- key 相同 → 复用现有 DOM（patch 更新）
- key 不同 → 销毁旧节点、创建新节点

### 1.2 key 的核心功能

| 功能 | 说明 |
| --- | --- |
| **节点身份标识** | 在 diff 时判断新旧节点是否对应 |
| **高效复用** | key 相同的节点复用 DOM，避免重建 |
| **正确排序** | 列表顺序变化时，按 key 移动而非重建 |
| **状态保持** | 组件 key 不变时，保留内部状态（输入、滚动位置等） |
| **触发过渡** | key 变化触发 Transition 过渡动画 |

### 1.3 key 的基本用法

```vue
<template>
  <!-- ① v-for 列表：必须使用 key（推荐） -->
  <li v-for="item in items" :key="item.id">{{ item.name }}</li>

  <!-- ② 单个元素/组件：可选，用于强制替换或状态管理 -->
  <UserProfile :key="userId" :user="user" />

  <!-- ③ Transition 过渡：key 变化触发动画 -->
  <Transition>
    <div :key="currentStep">{{ currentStep }}</div>
  </Transition>

  <!-- ④ 配合 <template v-for> -->
  <template v-for="item in list" :key="item.id">
    <dt>{{ item.term }}</dt>
    <dd>{{ item.desc }}</dd>
  </template>
</template>
```

---

## 二、key 与 diff 算法

### 2.1 虚拟 DOM 与 diff

Vue 渲染流程：

```
数据变化
   ↓
生成新的虚拟 DOM 树（VNode）
   ↓
diff 算法：对比新旧 VNode 树
   ↓
最小化更新真实 DOM
```

**虚拟 DOM（VNode）结构**：

```typescript
interface VNode {
  type: string | Component  // 标签名或组件
  props: object             // 属性（含 key）
  key: string | number | symbol | null  // key 值
  children: VNode[]         // 子节点
  el: Node | null           // 对应的真实 DOM
  // ...
}
```

### 2.2 同层比较原则

Vue 的 diff 算法遵循**同层比较**原则：

```
         旧 VNode 树              新 VNode 树
           root                    root
          /    \                  /    \
        A       B                A       C
       / \                      / \
      A1  A2                   A1  A2
```

- **只比较同一层级的节点**：root 与 root 比，A 与 A 比，A1 与 A1 比
- **不跨层级比较**：如果节点层级变化，直接销毁重建
- **比较依据**：节点类型（type）+ key

### 2.3 key 在 diff 中的作用

diff 判断两个节点是否"相同"的逻辑：

```typescript
function isSameVNodeType(n1: VNode, n2: VNode): boolean {
  // 类型相同 且 key 相同 才认为是同一节点
  return n1.type === n2.type && n1.key === n2.key
}
```

```
┌──────────────────────────────────────────────────────┐
│              节点是否"相同"的判断                       │
├──────────────────────────────────────────────────────┤
│                                                      │
│  旧节点 { type: 'div', key: 'a' }                    │
│  新节点 { type: 'div', key: 'a' }  → ✅ 相同（复用） │
│                                                      │
│  旧节点 { type: 'div', key: 'a' }                    │
│  新节点 { type: 'div', key: 'b' }  → ❌ 不同（重建） │
│                                                      │
│  旧节点 { type: 'div', key: 'a' }                    │
│  新节点 { type: 'span', key: 'a' } → ❌ 不同（重建） │
│                                                      │
│  旧节点 { type: 'div', key: null }                   │
│  新节点 { type: 'div', key: null } → ✅ 相同（复用） │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### 2.4 有 key vs 无 key 的 diff 流程

#### 无 key 的 diff（patchUnkeyedChildren）

```vue
<!-- 无 key -->
<div v-for="item in list">{{ item.name }}</div>
```

```
旧：[A, B, C]
新：[B, C, D]

无 key 的 diff（按索引比较）：
  索引 0: A → B  （patch 更新：A 变 B）
  索引 1: B → C  （patch 更新：B 变 C）
  索引 2: C → D  （patch 更新：C 变 D）

问题：
  - 3 次 patch 操作
  - A 本应销毁，却变成 B（DOM 复用错误）
  - 如果 A 是组件，内部状态会被错误保留
```

#### 有 key 的 diff（patchKeyedChildren）

```vue
<!-- 有 key -->
<div v-for="item in list" :key="item.id">{{ item.name }}</div>
```

```
旧：[A(key=1), B(key=2), C(key=3)]
新：[B(key=2), C(key=3), D(key=4)]

有 key 的 diff（按 key 匹配）：
  - key=1（A）：旧有新无 → 销毁 A
  - key=2（B）：位置前移 → 移动 B
  - key=3（C）：位置前移 → 移动 C
  - key=4（D）：新有旧无 → 创建 D

操作：
  - 1 次销毁（A）
  - 2 次移动（B、C）
  - 1 次创建（D）
  - 0 次 patch（节点内容未变）
```

**对比总结**：

| 场景 | 无 key | 有 key |
| --- | --- | --- |
| 列表顺序变化 | patch 所有节点（内容更新） | 移动节点（DOM 操作少） |
| 节点内容相同 | 仍 patch（浪费） | 不 patch（高效） |
| 组件状态 | 错误复用（状态混乱） | 正确保留对应状态 |
| 性能 | 列表大时差 | 更优 |

---

## 三、key 工作原理详解

### 3.1 patchKeyedChildren 算法

Vue3 的有 key diff 算法（`patchKeyedChildren`）采用**首尾双向指针 + 中间乱序处理**：

```typescript
// 简化的 patchKeyedChildren 算法
function patchKeyedChildren(c1: VNode[], c2: VNode[]) {
  let i = 0                          // 从头指针
  let e1 = c1.length - 1             // 旧列表尾指针
  let e2 = c2.length - 1             // 新列表尾指针
  
  // ① 从头同步（相同前缀）
  while (i <= e1 && i <= e2) {
    if (isSameVNodeType(c1[i], c2[i])) {
      patch(c1[i], c2[i])            // 相同，patch 更新
      i++
    } else {
      break
    }
  }
  
  // ② 从尾同步（相同后缀）
  while (i <= e1 && i <= e2) {
    if (isSameVNodeType(c1[e1], c2[e2])) {
      patch(c1[e1], c2[e2])          // 相同，patch 更新
      e1--
      e2--
    } else {
      break
    }
  }
  
  // ③ 旧列表遍历完，新列表有剩余 → 挂载新节点
  if (i > e1) {
    if (i <= e2) {
      while (i <= e2) {
        mount(c2[i])                 // 挂载
        i++
      }
    }
  }
  // ④ 新列表遍历完，旧列表有剩余 → 卸载旧节点
  else if (i > e2) {
    while (i <= e1) {
      unmount(c1[i])                 // 卸载
      i++
    }
  }
  // ⑤ 中间部分乱序 → 重建 + 移动
  else {
    // 复杂的中间处理（见下文）
    patchUnknownChildren(c1, c2, i, e1, e2)
  }
}
```

### 3.2 五步 diff 流程

```
旧：[a, b, c, d, e, f, g]
新：[a, b, e, c, d, h, f, g]

Step 1：从头同步
  i=0  a vs a → 相同，patch，i=1
  i=1  b vs b → 相同，patch，i=2
  i=2  c vs e → 不同，break
  结果：[a✓, b✓, c, d, e, f, g] → [a✓, b✓, e, c, d, h, f, g]

Step 2：从尾同步
  e1=6  g vs g → 相同，patch，e1=5, e2=7
  e1=5  f vs f → 相同，patch，e1=4, e2=6
  e1=4  e vs h → 不同，break
  结果：[a✓, b✓, c, d, e, f✓, g✓] → [a✓, b✓, e, c, d, h, f✓, g✓]

Step 3：判断剩余
  i=2, e1=4, e2=6 → 新旧都有剩余（中间乱序）

Step 4：处理中间乱序部分
  旧剩余：[c, d, e]（索引 2-4）
  新剩余：[e, c, d, h]（索引 2-6）
  
  4.1 为新节点建立 key → 索引映射
      Map { e:0, c:1, d:2, h:3 }
  
  4.2 遍历旧剩余，在新映射中查找
      c → 找到（新索引 1），patch，可复用
      d → 找到（新索引 2），patch，可复用
      e → 找到（新索引 0），patch，可复用
  
  4.3 新节点 h 未匹配 → 挂载
  
  4.4 计算最长递增子序列（LIS）确定需移动的节点
      复用节点的新位置：[0, 1, 2]（e, c, d）
      LIS = [0, 1, 2]（全部递增，无需移动？）
      实际需根据位置变化判断移动

Step 5：移动/挂载/卸载
  - h：新节点，挂载
  - c, d, e：移动到正确位置
```

**最长递增子序列（LIS）的作用**：

```
LIS 用于最小化 DOM 移动操作：
- 在 LIS 中的节点不需要移动（相对顺序正确）
- 不在 LIS 中的节点需要移动

示例：
旧位置：[c(0), d(1), e(2)]
新位置：[e(0), c(1), d(2)]

e 的新位置 0 < c 的新位置 1 < d 的新位置 2
但旧顺序是 c → d → e，新顺序是 e → c → d

LIS 计算：找到不需要移动的节点子序列
移动最少节点使整体有序
```

### 3.3 复用与重建的本质

```vue
<script setup>
import { ref } from 'vue'

const items = ref([
  { id: 1, name: '张三' },
  { id: 2, name: '李四' },
  { id: 3, name: '王五' },
])

// 删除第二个
function remove() {
  items.value.splice(1, 1)  // 删除李四
}
</script>

<template>
  <!-- key 用 id -->
  <div v-for="item in items" :key="item.id">
    {{ item.name }}
  </div>
</template>
```

**删除李四后的 diff**：

```
旧：[张三(id=1), 李四(id=2), 王五(id=3)]
新：[张三(id=1), 王五(id=3)]

diff 过程：
  从头：张三 vs 张三 → 相同（id=1），patch，i=1
  从尾：王五 vs 王五 → 相同（id=3），patch
  
  剩余：旧 [李四(id=2)]，新 []（无）
  → 卸载李四

结果：
  - 张三：复用（patch）
  - 王五：复用（patch）
  - 李四：卸载
  - 无需移动 DOM
```

**若用 index 作为 key 的错误**：

```
旧：[张三(key=0), 李四(key=1), 王五(key=2)]
新：[张三(key=0), 王五(key=1)]

diff 过程（按 key=index 匹配）：
  key=0：张三 vs 张三 → 相同，patch
  key=1：李四 vs 王五 → key 相同，patch（李四的 DOM 变成王五）
  key=2：王五 → 旧有新无 → 卸载

结果（错误）：
  - 李四的 DOM 被改成王五（内容更新）
  - 原王五的 DOM 被卸载
  - 若李四是组件（含输入状态），状态被错误保留到王五
```

---

## 四、key 值类型对比

### 4.1 字符串 key

```vue
<template>
  <!-- 字符串 key：最常用 -->
  <div v-for="user in users" :key="user.id">{{ user.name }}</div>
</template>
```

**特点**：
- ✅ 最常用，可读性好
- ✅ 稳定性强（id 通常不变）
- ✅ 序列化友好（JSON 存储）
- ⚠️ 需确保全局或列表内唯一

### 4.2 数字 key

```vue
<template>
  <!-- 数字 key -->
  <div v-for="item in items" :key="item.numericId">{{ item.name }}</div>
</template>
```

**特点**：
- ✅ 性能略优（数字比较比字符串快）
- ✅ 适合自增 ID 场景
- ⚠️ 注意 0 和 '0' 的区别（Vue 会做类型转换）

### 4.3 Symbol key

```vue
<script setup>
import { ref } from 'vue'

// Symbol 作为 key
const items = ref([
  { id: Symbol('item1'), name: '张三' },
  { id: Symbol('item2'), name: '李四' },
])
</script>

<template>
  <!-- Symbol key -->
  <div v-for="item in items" :key="item.id">{{ item.name }}</div>
</template>
```

**特点**：
- ✅ 绝对唯一（即使描述相同）
- ✅ 适合无稳定 ID 的临时列表
- ❌ 不可序列化（不能存 JSON）
- ❌ 每次创建都是新 Symbol，不适合从数据生成
- ⚠️ 谨慎使用，通常不推荐

### 4.4 类型选择建议

| 场景 | 推荐 key 类型 | 示例 |
| --- | --- | --- |
| 数据库记录 | 字符串/数字 ID | `item.id` |
| 后端返回数据 | 字符串 UUID | `item.uuid` |
| 前端生成数据 | 数字自增 | `++counter` |
| 临时列表 | Symbol | `Symbol()` |
| 静态列表 | 字符串 | `'header'` |

**类型一致性原则**：同一列表的 key 必须类型一致。

```vue
<!-- ❌ 错误：key 类型混合 -->
<div v-for="item in list" :key="item.id">  <!-- id 有时是数字，有时是字符串 -->

<!-- ✅ 正确：统一类型 -->
<div v-for="item in list" :key="String(item.id)">
```

---

## 五、常见使用误区

### 5.1 用 index 作为 key

**最常见也最危险的误区**：

```vue
<!-- ❌ 错误：用 index 作为 key -->
<template>
  <div v-for="(item, index) in list" :key="index">
    {{ item.name }}
  </div>
</template>
```

**问题 1：数据错位**

```javascript
const list = ref([
  { name: '张三' },
  { name: '李四' },
  { name: '王五' },
])

// 在头部插入新元素
list.value.unshift({ name: '赵六' })
```

```
用 index 作 key 的 diff：
旧：[张三(key=0), 李四(key=1), 王五(key=2)]
新：[赵六(key=0), 张三(key=1), 李四(key=2), 王五(key=3)]

diff 结果（错误）：
  key=0：张三 → 赵六（patch，内容更新）
  key=1：李四 → 张三（patch，内容更新）
  key=2：王五 → 李四（patch，内容更新）
  key=3：新挂载王五

本应只插入 1 个，却变成 4 次操作 + 状态错乱
```

**问题 2：组件状态混乱**

```vue
<!-- 输入框组件 -->
<template>
  <div v-for="(item, index) in list" :key="index">
    <input v-model="item.name" placeholder="姓名" />
    <span>其他状态：{{ item.status }}</span>
  </div>
</template>
```

```
场景：在第一个输入框输入"测试"，然后 unshift 新元素

用 index 作 key：
  - 输入框 DOM 被复用（key=0 不变）
  - 但绑定的数据从张三变成赵六
  - 输入框显示"测试"（DOM 状态保留），但数据是赵六
  - 状态与数据不一致！

用 id 作 key：
  - 张三的 DOM 移动到 key=1
  - 赵六的 DOM 新建 key=0
  - 输入框状态与数据正确对应
```

**何时可以用 index**：
- 列表纯展示（无输入、无组件状态）
- 列表不会增删排序
- 静态列表

### 5.2 用随机数作为 key

```vue
<!-- ❌ 错误：用随机数作为 key -->
<template>
  <div v-for="item in list" :key="Math.random()">
    {{ item.name }}
  </div>
</template>
```

**问题**：每次渲染都生成新 key → 每次都重建 DOM → 性能极差 + 状态丢失。

```vue
<!-- ❌ 错误：用 Date.now() -->
<div v-for="item in list" :key="Date.now()">{{ item.name }}</div>
```

### 5.3 用对象引用作为 key

```vue
<!-- ❌ 错误：用对象引用 -->
<template>
  <div v-for="item in list" :key="item">{{ item.name }}</div>
</template>
```

**问题**：对象引用作为 key 会被转成 `[object Object]`，所有节点 key 相同。

### 5.4 key 不唯一

```vue
<!-- ❌ 错误：key 重复 -->
<template>
  <div v-for="item in list" :key="item.type">
    {{ item.name }}
  </div>
</template>

<script setup>
const list = ref([
  { type: 'A', name: '张三' },
  { type: 'A', name: '李四' },  // type 重复！
])
</script>
```

**后果**：Vue 会警告 `'Duplicate keys detected'`，diff 行为不确定。

### 5.5 动态修改 key

```vue
<!-- ❌ 错误：key 动态变化 -->
<template>
  <div v-for="item in list" :key="item.id + Date.now()">
    {{ item.name }}
  </div>
</template>
```

**问题**：key 每次渲染都变 → 每次都重建 DOM。

---

## 六、特殊场景应用

### 6.1 动画过渡

`key` 变化会触发 `<Transition>` 的过渡动画：

```vue
<template>
  <!-- 切换步骤时触发淡入淡出 -->
  <Transition name="fade" mode="out-in">
    <div :key="currentStep" class="step-content">
      {{ steps[currentStep] }}
    </div>
  </Transition>
  
  <button @click="next">下一步</button>
</template>

<script setup>
import { ref } from 'vue'

const steps = ['第一步', '第二步', '第三步']
const currentStep = ref(0)

function next() {
  currentStep.value = (currentStep.value + 1) % steps.length
}
</script>

<style>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
```

**原理**：key 变化 → Vue 认为是不同节点 → 旧节点 leave + 新节点 enter → 触发过渡。

### 6.2 组件状态保持

用 key 保持组件实例，避免重复创建：

```vue
<template>
  <!-- ❌ 错误：切换 tab 时组件重建，状态丢失 -->
  <component :is="currentTab" />
  
  <!-- ✅ 正确：用 key 标识，配合 v-show 或 keep-alive -->
  <KeepAlive>
    <component :is="currentTab" :key="currentTab" />
  </KeepAlive>
</template>
```

**用户详情页场景**：

```vue
<template>
  <!-- 切换用户时，强制重新创建组件（清空旧用户状态） -->
  <UserProfile :key="selectedUserId" :user="selectedUser" />
</template>

<script setup>
import { ref } from 'vue'

const selectedUserId = ref(null)

function selectUser(id) {
  selectedUserId.value = id  // key 变化 → 组件重建 → 状态重置
}
</script>
```

### 6.3 强制重新渲染

通过改变 key 强制组件重新渲染：

```vue
<template>
  <!-- 改变 key 强制重渲染（常用于第三方组件刷新） -->
  <ECharts :key="chartKey" :option="chartOption" />
  <button @click="refresh">刷新图表</button>
</template>

<script setup>
import { ref } from 'vue'

const chartKey = ref(0)

function refresh() {
  chartKey.value++  // key 变化 → ECharts 组件重建
}
</script>
```

### 6.4 表单输入重置

通过 key 重置表单：

```vue
<template>
  <UserForm :key="formKey" :initial-data="initialData" @submit="handleSubmit" />
  <button @click="resetForm">重置表单</button>
</template>

<script setup>
import { ref } from 'vue'

const formKey = ref(0)
const initialData = ref({ name: '', age: '' })

function resetForm() {
  formKey.value++  // key 变化 → 表单组件重建 → 输入清空
}

function handleSubmit(data) {
  // 提交后重置
  formKey.value++
}
</script>
```

### 6.5 keep-alive 缓存

`<KeepAlive>` 通过 key（或组件 name）缓存组件实例：

```vue
<template>
  <KeepAlive :max="5">
    <component :is="currentComponent" :key="currentId" />
  </KeepAlive>
</template>

<script setup>
import { ref } from 'vue'

const currentComponent = ref('UserDetail')
const currentId = ref(1)

// 不同 id 视为不同实例，分别缓存
function switchUser(id) {
  currentId.value = id  // key 变化 → 新实例缓存（旧实例保留）
}
</script>
```

**原理**：KeepAlive 内部用 key 作为缓存 Map 的键，key 不同则缓存不同实例。

---

## 七、最佳实践

### 7.1 key 选择原则

```
key 选择决策树：

数据有唯一 ID？
  ├─ 是 → 用 ID（字符串/数字）
  └─ 否 → 能否生成稳定 ID？
            ├─ 能 → 用生成的 ID（如 nanoid）
            └─ 否 → 列表是否纯展示？
                      ├─ 是 → 可用 index（不推荐）
                      └─ 否 → 用 Symbol（临时列表）
```

**原则**：
1. **稳定**：key 在数据生命周期内不变
2. **唯一**：同列表内 key 不重复
3. **可预测**：相同数据始终生成相同 key

### 7.2 代码规范

```vue
<template>
  <!-- ✅ 推荐：用业务 ID -->
  <div v-for="user in users" :key="user.id">
    {{ user.name }}
  </div>

  <!-- ✅ 推荐：复杂对象用组合 key（确保唯一） -->
  <div v-for="item in list" :key="`${item.type}_${item.id}`">
    {{ item.name }}
  </div>

  <!-- ✅ 推荐：template v-for 也要 key -->
  <template v-for="item in list" :key="item.id">
    <dt>{{ item.term }}</dt>
    <dd>{{ item.desc }}</dd>
  </template>
</template>
```

**无稳定 ID 时生成 ID**：

```javascript
import { nanoid } from 'nanoid'

// 数据初始化时生成 ID
const list = ref(rawData.map(item => ({
  ...item,
  _uid: nanoid(),  // 生成稳定唯一 ID
})))
```

### 7.3 性能优化

```vue
<template>
  <!-- ✅ 大列表用 key 优化 diff -->
  <div v-for="item in largeList" :key="item.id">
    {{ item.name }}
  </div>
</template>

<script setup>
// ✅ 用唯一 ID 而非 index，减少不必要 patch
// ✅ 用虚拟滚动配合 key（vue-virtual-scroller）
import { RecycleScroller } from 'vue-virtual-scroller'
</script>
```

**key 与性能的关系**：

| 场景 | 无 key | 有 key（正确） |
| --- | --- | --- |
| 列表头部插入 | 全部 patch（O(n)） | 1 次挂载 + 移动（O(1)~O(n)） |
| 列表排序 | 全部 patch（O(n)） | 移动节点（DOM 操作少） |
| 删除中间项 | 后续全部 patch | 1 次卸载 |
| 大列表渲染 | 慢 | 快 |

---

## 八、FAQ

### Q1: v-for 一定要写 key 吗？

**A**: Vue3 中 key 是**可选**的（不写不报错），但**强烈推荐**写。不写 key 时 Vue 按 index 处理，在列表增删排序时会出现状态错乱和性能问题。

### Q2: key 可以用对象属性吗？

**A**: 可以，但需是基本类型（字符串/数字/Symbol）。对象引用会被转成 `[object Object]`。

```vue
<!-- ✅ -->
<div v-for="item in list" :key="item.id">

<!-- ❌ -->
<div v-for="item in list" :key="item">
```

### Q3: key 变化会触发什么？

**A**: key 变化 → Vue 认为是不同节点 → 旧节点卸载 + 新节点挂载。常用于强制重渲染、触发动画、重置组件状态。

### Q4: 为什么用 index 作 key 有时"看起来正常"？

**A**: 当列表**仅追加**（push）且**纯展示**（无组件状态）时，index 作 key 行为正确。但一旦涉及头部插入、删除、排序，或含输入组件，就会出问题。建议始终用稳定 ID。

### Q5: key 与 v-if 的关系？

**A**: `v-if` 切换不同类型节点时，无需 key（类型不同自动重建）。但同类型节点切换时，可用 key 强制重建：

```vue
<!-- 不同类型：无需 key -->
<div v-if="type === 'A'">A</div>
<span v-else>B</span>

<!-- 同类型：用 key 强制重建 -->
<div v-if="type === 'A'" key="a">A</div>
<div v-else key="b">B</div>
```

### Q6: 动态生成的数据如何保证 key 稳定？

**A**: 数据创建时即生成 ID，而非渲染时：

```javascript
// ❌ 错误：渲染时生成
<div v-for="item in list" :key="Math.random()">

// ✅ 正确：创建时生成
const newItem = { id: nanoid(), name: '张三' }
list.value.push(newItem)
```

---

## 附录 源码索引

Vue3 中 key 相关源码位于 `packages/runtime-core/src/`：

| 文件 | 核心内容 |
| --- | --- |
| `vnode.ts` | VNode 类型定义（含 key 字段）、`isSameVNodeType` 判断 |
| `renderer.ts` | `patchKeyedChildren`（有 key diff）、`patchUnkeyedChildren`（无 key diff） |
| `helpers/resolveAssets.ts` | key 在组件解析中的作用 |
| `components/KeepAlive.ts` | KeepAlive 用 key 缓存组件实例 |

**核心函数**：
- `isSameVNodeType(n1, n2)`：判断节点是否相同（type + key）
- `patchKeyedChildren(c1, c2, container)`：有 key 的 diff 算法
- `patchUnkeyedChildren(c1, c2, container)`：无 key 的 diff 算法
- `move(vnode, container, anchor)`：移动节点
- `unmount(vnode)`：卸载节点
- `mountElement(vnode, container)`：挂载节点

**patchKeyedChildren 五步算法**：
1. **Sync from start**：从头同步相同前缀
2. **Sync from end**：从尾同步相同后缀
3. **Common sequence + mount**：旧遍历完，新有剩余 → 挂载
4. **Common sequence + unmount**：新遍历完，旧有剩余 → 卸载
5. **Unknown sequence**：中间乱序 → key 映射 + LIS + 移动

---

## 参考资料

- Vue3 key 官方文档：https://cn.vuejs.org/api/special-attributes.html#key
- Vue3 列表渲染：https://cn.vuejs.org/guide/essentials/list.html#maintaining-state-with-key
- Vue3 Transition：https://cn.vuejs.org/guide/built-ins/transition.html
- Vue3 KeepAlive：https://cn.vuejs.org/guide/built-ins/keep-alive.html
- Vue3 源码 renderer.ts：https://github.com/vuejs/core/blob/main/packages/runtime-core/src/renderer.ts
- Vue3 虚拟 DOM：https://cn.vuejs.org/guide/extras/rendering-mechanism.html

---

> **文档说明**：本文档共 8 大章节 + 附录 + 参考资料，系统覆盖 Vue3 key 属性的概念、原理、使用、误区与最佳实践。核心要点：① key 是节点身份标识，相同 key 复用 DOM；② v-for 推荐用稳定唯一 ID 作 key，避免用 index；③ key 变化触发节点重建，可用于强制重渲染、动画、状态重置。建议结合 Vue3 源码 `renderer.ts` 的 `patchKeyedChildren` 深入理解 diff 算法。
