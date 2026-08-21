# Web 性能优化完整指南

> 本文档系统阐述前端性能优化的核心方法论，涵盖 Chrome DevTools Performance 面板使用教程与 Web 核心性能指标（LCP / CLS / INP）的深度解析。

---
https://www.cnblogs.com/keshizhidao/articles/20049125#1
## 目录

- [第一部分：Chrome DevTools Performance 标签页完整使用指南](#第一部分chrome-devtools-performance-标签页完整使用指南)
  - [一、Performance 面板界面组成与功能分布](#一performance-面板界面组成与功能分布)
  - [二、录制性能数据的完整步骤](#二录制性能数据的完整步骤)
  - [三、性能数据分析详解](#三性能数据分析详解)
  - [四、识别常见性能瓶颈](#四识别常见性能瓶颈)
  - [五、性能问题优化建议与实施步骤](#五性能问题优化建议与实施步骤)
- [第二部分：Web 核心性能指标深度解析](#第二部分web-核心性能指标深度解析)
  - [六、LCP — Largest Contentful Paint](#六lcp--largest-contentful-paint)
  - [七、CLS — Cumulative Layout Shift](#七cls--cumulative-layout-shift)
  - [八、INP — Interaction to Next Paint](#八inp--interaction-to-next-paint)
- [第三部分：实战案例分析](#第三部分实战案例分析)
  - [案例一：电商首页 LCP 优化](#案例一电商首页-lcp-优化)
  - [案例二：内容资讯站 CLS 优化](#案例二内容资讯站-cls-优化)
  - [案例三：SPA 应用 INP 优化](#案例三spa-应用-inp-优化)
- [第四部分：性能测试环境配置与持续优化](#第四部分性能测试环境配置与持续优化)
  - [九、性能测试环境配置建议](#九性能测试环境配置建议)
  - [十、性能监控与持续优化方法论](#十性能监控与持续优化方法论)
- [附录](#附录)

---

# 第一部分：Chrome DevTools Performance 标签页完整使用指南

## 一、Performance 面板界面组成与功能分布

### 1.1 打开 Performance 面板

1. 打开 Chrome 浏览器，访问目标页面
2. 按 `F12` 或 `Ctrl + Shift + I`（macOS: `Cmd + Option + I`）打开 DevTools
3. 点击顶部 **Performance** 标签页

> 💡 快捷方式：`Ctrl + Shift + E` 可直接打开 Performance 面板并开始录制

<!-- 截图：Performance面板整体界面 -->
> 📷 截图参考：`assets/performance-01-panel-overview.png` — Performance 面板整体界面

### 1.2 面板区域划分

Performance 面板自上而下由以下区域组成：

```
┌─────────────────────────────────────────────────────────┐
│  工具栏（Toolbar）                                        │
│  [录制] [刷新录制] [清除] [缩放] [筛选] [设置]             │
├─────────────────────────────────────────────────────────┤
│  概览面板（Overview Panel）                               │
│  ┌──────────────┬──────────────┬──────────────┐          │
│  │   FPS 图表    │  CPU 图表    │  NET 图表    │          │
│  └──────────────┴──────────────┴──────────────┘          │
├─────────────────────────────────────────────────────────┤
│  火焰图区域（Flame Chart / Waterfall）                    │
│  ├── Network（网络请求瀑布图）                             │
│  ├── Interactions（用户交互）                             │
│  ├── Main（主线程活动）                                   │
│  ├── GPU                                                 │
│  ├── Compositor                                         │
│  ├── Raster（光栅化）                                     │
│  └── ...其他线程                                         │
├─────────────────────────────────────────────────────────┤
│  详细面板（Bottom-Up / Call Tree / Event Log）            │
│  ┌─────────┬──────────┬──────────┐                       │
│  │Bottom-Up│Call Tree │Event Log │                       │
│  └─────────┴──────────┴──────────┘                       │
└─────────────────────────────────────────────────────────┘
```

### 1.3 各区域功能说明

| 区域 | 功能 | 核心用途 |
|------|------|----------|
| **工具栏** | 录制控制、缩放、筛选 | 开始/停止录制，配置录制选项 |
| **概览面板** | FPS/CPU/NET 时间线缩略图 | 快速定位性能瓶颈时间点 |
| **FPS 图表** | 每秒帧数可视化 | 识别掉帧区域（绿色=正常，红色=卡顿） |
| **CPU 图表** | CPU 占用率 | 判断 CPU 是否满载 |
| **NET 图表** | 网络活动概览 | 观察请求并发与阻塞情况 |
| **火焰图区域** | 各线程详细活动时间线 | 定位具体函数调用与执行时长 |
| **详细面板** | 三种分析视图 | 量化性能开销的来源 |

<!-- 截图：各区域标注 -->
> 📷 截图参考：`assets/performance-02-panel-regions.png` — Performance 面板各区域标注

---

## 二、录制性能数据的完整步骤

### 2.1 配置录制选项

点击工具栏的 ⚙️（Settings）按钮，可配置以下选项：

| 选项 | 说明 | 推荐设置 |
|------|------|----------|
| **Network** | 网络节流 | 模拟真实用户环境，选择 `Slow 3G` / `Fast 3G` |
| **CPU** | CPU 降速 | 开启 `6x slowdown` 模拟低端设备 |
| **Screenshots** | 录制截图 | ✅ 开启，用于回放页面变化 |
| **Memory** | 内存分配 | 按需开启（会增加录制开销） |
| **Web Vitals** | 核心指标标记 | ✅ 开启，自动标记 LCP/CLS 等关键节点 |

<!-- 截图：录制设置面板 -->
> 📷 截图参考：`assets/performance-03-record-settings.png` — 录制配置选项

### 2.2 执行录制的最佳实践

#### 页面加载性能录制

```
步骤：
1. 打开 DevTools → Performance 面板
2. 确保勾选 Screenshots 和 Web Vitals
3. 设置 Network 节流（如 Fast 3G）
4. 点击 🔴 录制按钮
5. 立即在地址栏输入 URL 并回车
6. 等待页面完全加载（观察 Network 面板请求完成）
7. 点击 ⏹ 停止录制
```

> 💡 更便捷的方式：点击工具栏的 **🔄 刷新录制** 按钮，会自动刷新页面并录制加载过程

#### 交互性能录制

```
步骤：
1. 页面已加载完成
2. 点击 🔴 开始录制
3. 执行目标交互操作（如点击按钮、滚动页面、输入文字）
4. 等待操作完成及页面响应
5. 点击 ⏹ 停止录制
```

#### 录制注意事项

- **录制时长**：单次录制建议控制在 **10-30 秒**，过长会导致数据量过大难以分析
- **干扰消除**：录制前关闭无关浏览器扩展，使用隐身模式减少干扰
- **多次录制**：同一场景至少录制 3 次取典型结果，排除偶然因素
- **禁用缓存**：加载性能测试时勾选 `Disable cache`，确保每次都从网络获取资源

<!-- 截图：录制过程 -->
> 📷 截图参考：`assets/performance-04-recording.png` — 录制过程中的 Performance 面板

### 2.3 设置性能指标关注点

录制前应明确分析目标：

| 分析目标 | 关注区域 | 录制方式 |
|----------|----------|----------|
| 页面加载速度 | Main 线程 + Network | 刷新录制 |
| JavaScript 执行阻塞 | Main 线程火焰图 | 交互录制 |
| 渲染性能 | Rendering 轨道 + FPS | 滚动/动画录制 |
| 内存泄漏 | Memory 面板配合 | 长时间交互录制 |
| 网络瀑布图 | Network 轨道 | 刷新录制 |

---

## 三、性能数据分析详解

### 3.1 火焰图（Flame Chart）

火焰图是 Performance 面板最核心的分析视图，展示函数调用的层级关系与执行时长。

#### 结构解读

```
火焰图结构（时间从左到右，调用层级从上到下）：

│ Task (长任务)                                              │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Evaluate Script                                        │ │
│ │ ┌──────────────────┐  ┌───────────────────────┐       │ │
│ │ │ Parse HTML       │  │ Execute JS             │       │ │
│ │ │ ┌─────────────┐ │  │ ┌───────────────────┐ │       │ │
│ │ │ │ DOM Builder │ │  │ │ renderList()      │ │       │ │
│ │ │ └─────────────┘ │  │ │ ┌───────────────┐ │ │       │ │
│ │ │                 │  │ │ │ createElement │ │ │       │ │
│ │ │                 │  │ │ └───────────────┘ │ │       │ │
│ │ └──────────────────┘  │ └───────────────────┘ │       │ │
│ │                       └───────────────────────┘       │ │
│ └────────────────────────────────────────────────────────┘ │
```

#### 关键概念

- **Task（任务）**：最顶层的灰色块，表示一个宏任务。长度超过 50ms 的任务被标记为**长任务（Long Task）**，右上角会出现红色三角 ⚠️
- **调用层级**：上层函数调用下层函数，宽度代表执行时间
- **颜色编码**：
  - 🟡 黄色：JavaScript 执行
  - 🟣 紫色：样式计算（Recalculate Style）和 布局（Layout）
  - 🟢 绿色：绘制（Paint）和 合成（Composite）
  - 🔵 蓝色：HTML 解析
  - ⚪ 灰色：其他/空闲

<!-- 截图：火焰图详解 -->
> 📷 截图参考：`assets/performance-05-flamechart.png` — 火焰图详解

#### 火焰图分析技巧

1. **寻找宽块**：横向宽度大 = 执行时间长，优先关注
2. **关注长任务**：带有红色标记的长任务是交互延迟的主要来源
3. **从上到下追踪**：顶层 Task → 中层业务函数 → 底层原生调用
4. **点击查看详情**：选中任意函数块，底部 Summary 面板显示详细信息

### 3.2 调用树（Call Tree）

调用树以自顶向下的层级结构展示函数调用及耗时，适合量化各函数的性能开销。

#### 视图切换

在详细面板选择 **Call Tree** 标签：

| 列名 | 含义 |
|------|------|
| **Self Time** | 函数自身执行时间（不含子函数） |
| **Total Time** | 函数总执行时间（含子函数） |
| **Activity** | 函数/活动名称 |

#### 分析方法

```
按 Total Time 降序排列，找出耗时最长的调用链：

Top-Down 视图：
┌──────────────────────┬───────────┬────────────┐
│ Activity             │ Self Time │ Total Time │
├──────────────────────┼───────────┼────────────┤
│ Task                 │   0.1ms   │  850ms     │  ← 总入口
│  └─ Evaluate Script  │   2ms     │  849ms     │
│     └─ renderPage()  │   5ms     │  840ms     │  ← 核心瓶颈
│        └─ fetchData()│   800ms   │  800ms     │  ← 数据获取耗时
│        └─ render()   │   35ms    │  35ms      │
└──────────────────────┴───────────┴────────────┘
```

**关键技巧**：
- 按 `Total Time` 排序，快速定位耗时最大的调用链
- 按 `Self Time` 排序，找出自身执行最耗时的函数（非子函数耗时）
- 使用搜索框过滤特定函数名

### 3.3 性能摘要（Summary）

Summary 标签提供录制时段的总体时间分布饼图：

| 分类 | 颜色 | 含义 | 优化方向 |
|------|------|------|----------|
| **Loading** | 蓝色 | 网络请求与 HTML 解析 | 资源压缩、CDN、预加载 |
| **Scripting** | 黄色 | JavaScript 编译与执行 | 代码拆分、懒加载、Web Workers |
| **Rendering** | 紫色 | 样式计算与布局 | 减少 DOM 操作、避免强制同步布局 |
| **Painting** | 绿色 | 绘制与合成 | 减少重绘区域、使用 CSS 动画 |
| **System** | 灰色 | Chrome 内部开销 | 通常不可优化 |
| **Idle** | 白色 | 空闲 | — |

<!-- 截图：Summary饼图 -->
> 📷 截图参考：`assets/performance-06-summary.png` — Summary 性能摘要饼图

**分析策略**：Scripting 占比超过 50% 时应重点优化 JS；Rendering 占比过高时需检查布局抖动。

### 3.4 Bottom-Up 视图

从最底层的函数向上聚合，展示哪些函数在整体中消耗最多时间。

```
Bottom-Up 视图（按 Self Time 排序）：

┌────────────────────────┬───────────┬────────────┬─────────┐
│ Activity               │ Self Time │ Total Time │ 占比     │
├────────────────────────┼───────────┼────────────┼─────────┤
│ XMLHttpRequest.send    │  450ms    │  450ms     │  35.2%  │  ← 最大瓶颈
│ CSS.recalculateStyle   │  280ms    │  280ms     │  21.9%  │
│ GC.collectGarbage      │  120ms    │  120ms     │   9.4%  │
│ DOM.createElement      │   85ms    │   85ms     │   6.6%  │
│ Layout                 │   65ms    │   65ms     │   5.1%  │
└────────────────────────┴───────────┴────────────┴─────────┘
```

**适用场景**：当你不知道性能瓶颈来自哪条调用链时，Bottom-Up 能帮你找到"无论谁调用，自身最耗时"的函数。

### 3.5 Event Log 视图

按时间顺序记录所有事件，适合排查特定时间点发生了什么。

```
Event Log 示例：

时间       │ 事件                        │ 耗时
00:00.000  │ Send Request GET /api/data  │ —
00:00.120  │ Receive Response            │ 120ms
00:00.125  │ Parse HTML                  │ 5ms
00:00.150  │ Evaluate Script app.js      │ 25ms
00:00.200  │ Recalculate Style           │ 50ms
00:00.260  │ Layout                      │ 10ms
00:00.280  │ Paint                       │ 20ms
```

---

## 四、识别常见性能瓶颈

### 4.1 JavaScript 执行阻塞

#### 症状

- Main 线程出现大块黄色区域（长任务 > 50ms）
- FPS 图表出现红色区域
- 用户交互（点击/输入）响应延迟

#### 常见原因

| 原因 | 火焰图特征 | 典型场景 |
|------|-----------|----------|
| 大量 DOM 操作 | 连续的 Layout/Paint 块 | 列表渲染、表格更新 |
| 复杂计算 | 单个宽黄色块 | 数据排序、加密运算 |
| 同步网络请求 | 宽黄色块中含 XHR | 初始化时同步加载数据 |
| 过多事件监听 | 重复的 Event Handler | scroll/resize 未节流 |
| 大体积 JS 解析 | Evaluate Script 过长 | 未拆分的 Bundle |

#### 诊断步骤

```
1. 在火焰图中定位长任务（灰色块右上角红色三角）
2. 展开调用栈，找到最宽的黄色块
3. 查看 Summary 中 Scripting 占比
4. 使用 Call Tree 的 Total Time 排序找到根因函数
```

<!-- 截图：JS阻塞火焰图 -->
> 📷 截图参考：`assets/performance-07-js-blocking.png` — JavaScript 执行阻塞的火焰图

### 4.2 渲染性能问题

#### 症状

- 紫色（Rendering）或绿色（Painting）区域占比过高
- FPS 图表频繁低于 60fps
- 动画卡顿、滚动不流畅

#### 常见原因

| 原因 | 诊断方法 | 影响 |
|------|----------|------|
| **强制同步布局（Layout Thrashing）** | 火焰图中紫块反复出现 | 读写 DOM 交替导致多次重排 |
| **布局抖动** | 连续的 Recalculate → Layout 循环 | 每帧重复计算布局 |
| **大面积重绘** | 绿色 Paint 块过宽 | 修改影响大面积的样式 |
| **复合层过多** | Composite Layers 耗时长 | 滥用 `will-change` 或 `transform` |
| **CSS 选择器复杂** | Recalculate Style 耗时长 | 嵌套过深的选择器 |

#### 诊断：识别强制同步布局

```javascript
// ❌ 强制同步布局示例（读写交替）
const elements = document.querySelectorAll('.item');
elements.forEach(el => {
  const height = el.offsetHeight;  // 读 → 触发布局计算
  el.style.height = height + 10 + 'px';  // 写 → 使布局失效
  // 下一次循环的读操作又会强制重新计算布局
});

// ✅ 优化：先批量读，再批量写
const elements = document.querySelectorAll('.item');
const heights = [];
elements.forEach(el => {
  heights.push(el.offsetHeight);  // 批量读
});
elements.forEach((el, i) => {
  el.style.height = heights[i] + 10 + 'px';  // 批量写
});
```

在火焰图中，强制同步布局表现为：`Layout` 被标记为 `⚠ Forced reflow`，出现紫色块中嵌套黄色脚本块的模式。

### 4.3 网络请求延迟

#### 症状

- Network 轨道中请求瀑布图过长
- 页面首屏加载慢
- 关键资源被非关键资源阻塞

#### 瀑布图分析

```
Network 瀑布图结构：

        0ms     200ms    400ms    600ms    800ms   1000ms
HTML    ████████████████
CSS     ───────────████████████████
JS      ────────────────────████████████████████████  ← 阻塞解析
Font    ─────────────────────────████████            ← 阻塞文本渲染
Image   ──────────────────────────────████████████   ← 非关键但占带宽
API     ───────────────────████████                  ← 数据依赖

问题分析：
1. CSS 阻塞了 JS 执行（JS 等待 CSS 下载+解析完成）
2. 字体阻塞了首屏文本渲染
3. 图片与关键资源竞争带宽
```

#### 关键瀑布图模式

| 模式 | 含义 | 优化方向 |
|------|------|----------|
| **瀑布过长** | 资源串行依赖 | 减少关键路径长度 |
| **空白间隙** | 未充分利用并发 | 使用 `preconnect` / `dns-prefetch` |
| **大块传输** | 资源体积过大 | 压缩、Tree Shaking、代码拆分 |
| **渲染阻塞** | CSS/字体阻塞 | 异步加载非关键 CSS、`font-display: swap` |

---

## 五、性能问题优化建议与实施步骤

### 5.1 JavaScript 优化

#### 代码拆分与懒加载

```javascript
// ❌ 优化前：一次性加载全部代码
import { HeavyComponent } from './heavy-component';
import { ChartLibrary } from './chart-lib';

// ✅ 优化后：动态导入按需加载
const loadHeavyComponent = async () => {
  const { HeavyComponent } = await import('./heavy-component');
  return HeavyComponent;
};

// 路由级别懒加载（React 示例）
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Settings = React.lazy(() => import('./pages/Settings'));
```

#### 长任务拆分

```javascript
// ❌ 优化前：长任务阻塞主线程
function processLargeArray(items) {
  const results = [];
  for (let i = 0; i < items.length; i++) {
    results.push(heavyComputation(items[i]));  // 1000项 × 1ms = 1s 长任务
  }
  return results;
}

// ✅ 优化后：使用 scheduler.yield() 拆分任务
async function processLargeArray(items) {
  const results = [];
  for (let i = 0; i < items.length; i++) {
    results.push(heavyComputation(items[i]));
    // 每处理 50 项让出主线程
    if (i % 50 === 0) {
      await new Promise(resolve => setTimeout(resolve, 0));
      // 或使用更现代的 API：
      // await scheduler.yield();
    }
  }
  return results;
}
```

#### Web Workers 卸载计算

```javascript
// main.js — 主线程
const worker = new Worker('compute-worker.js');

worker.postMessage({ data: largeDataset });

worker.onmessage = (event) => {
  const result = event.data;
  updateUI(result);  // 仅在计算完成后更新 UI
};

// compute-worker.js — Worker 线程
self.onmessage = (event) => {
  const { data } = event;
  const result = heavyComputation(data);
  self.postMessage(result);
};

function heavyComputation(data) {
  // 耗时计算不影响主线程
  return data.map(item => {
    // ... 复杂计算逻辑
  });
}
```

### 5.2 渲染优化

#### 使用 CSS 合成属性

```css
/* ❌ 触发 Layout + Paint 的属性 */
.animate-bad {
  transition: left 0.3s, top 0.3s;
  left: 100px;
  top: 50px;
}

/* ✅ 仅触发 Composite 的属性（GPU 加速） */
.animate-good {
  transition: transform 0.3s;
  transform: translate(100px, 50px);
}
```

| 属性 | 触发阶段 | 是否推荐动画 |
|------|----------|-------------|
| `transform` | Composite | ✅ 推荐 |
| `opacity` | Composite | ✅ 推荐 |
| `filter` | Composite | ✅ 推荐 |
| `width/height` | Layout → Paint → Composite | ❌ 避免 |
| `top/left` | Layout → Paint → Composite | ❌ 避免 |
| `margin/padding` | Layout → Paint → Composite | ❌ 避免 |
| `background-color` | Paint → Composite | ⚠️ 按需 |
| `box-shadow` | Paint → Composite | ⚠️ 按需 |

#### 虚拟列表

```javascript
// ❌ 渲染 10000 条数据
function renderList(data) {
  data.forEach(item => {
    const el = document.createElement('div');
    el.textContent = item.text;
    container.appendChild(el);  // 10000 次 DOM 操作
  });
}

// ✅ 虚拟列表：仅渲染可视区域
class VirtualList {
  constructor(container, items, itemHeight = 40) {
    this.container = container;
    this.items = items;
    this.itemHeight = itemHeight;
    this.visibleCount = Math.ceil(container.clientHeight / itemHeight);

    // 创建可视 DOM 池
    this.pool = [];
    for (let i = 0; i < this.visibleCount + 2; i++) {
      const el = document.createElement('div');
      el.style.height = itemHeight + 'px';
      container.appendChild(el);
      this.pool.push(el);
    }

    // 设置总高度撑开滚动条
    this.spacer = document.createElement('div');
    this.spacer.style.height = items.length * itemHeight + 'px';
    container.appendChild(this.spacer);

    container.addEventListener('scroll', () => this.render());
    this.render();
  }

  render() {
    const scrollTop = this.container.scrollTop;
    const startIndex = Math.floor(scrollTop / this.itemHeight);
    const offset = startIndex * this.itemHeight;

    this.pool.forEach((el, i) => {
      const dataIndex = startIndex + i;
      if (dataIndex < this.items.length) {
        el.textContent = this.items[dataIndex].text;
        el.style.transform = `translateY(${offset}px)`;
        el.style.position = 'absolute';
        el.style.display = '';
      } else {
        el.style.display = 'none';
      }
    });
  }
}
```

### 5.3 网络优化

```html
<!-- 资源优先级提示 -->
<head>
  <!-- 预连接：提前建立连接 -->
  <link rel="preconnect" href="https://cdn.example.com" />
  <link rel="dns-prefetch" href="https://api.example.com" />

  <!-- 预加载关键资源 -->
  <link rel="preload" href="/fonts/main-font.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="/js/critical.js" as="script" />

  <!-- 预获取下一页可能需要的资源 -->
  <link rel="prefetch" href="/js/about-page.js" />

  <!-- 非关键 CSS 异步加载 -->
  <link rel="preload" href="/css/non-critical.css" as="style"
        onload="this.onload=null;this.rel='stylesheet'" />
  <noscript><link rel="stylesheet" href="/css/non-critical.css" /></noscript>

  <!-- 非关键 JS 延迟加载 -->
  <script src="/js/analytics.js" defer></script>
  <script src="/js/chat-widget.js" async></script>
</head>
```

---

# 第二部分：Web 核心性能指标深度解析

> Web Vitals 是 Google 定义的一组衡量用户体验的核心指标。其中 **LCP、CLS、INP** 构成 **Core Web Vitals**，直接影响搜索引擎排名。

## 六、LCP — Largest Contentful Paint

### 6.1 定义

**LCP（最大内容绘制）** 衡量的是视口中最大的可见内容元素渲染到屏幕上的时间。它反映了用户感知到的页面**主要内容加载完成**的时刻。

### 6.2 哪些元素参与 LCP 计算

| 元素类型 | 示例 |
|----------|------|
| `<img>` | 图片 |
| `<image>` inside `<svg>` | SVG 内嵌图片 |
| `<video>` poster | 视频封面图 |
| 具有 `url()` 背景的元素 | CSS 背景图 |
| 块级文本元素 | `<p>`、`<h1>`、`<div>` 中的文字 |

> LCP 元素是上述元素中在视口中**面积最大**的那个。同一元素可能随页面加载变化（如小图加载完后大图替换成为 LCP 元素）。

### 6.3 行业标准值

```
         0ms          2500ms          4000ms
──────────┣━━━━━━━━━━━╋━━━━━━━━━━━━━╋──────────▶
           ┃   良好    ┃   需改进     ┃    差
           ┃  (Good)   ┃  (Needs     ┃  (Poor)
           ┃           ┃  Improvement)┃
        ≤ 2.5s      2.5s - 4s      > 4s
```

- **良好（Good）**：≤ 2.5 秒
- **需改进（Needs Improvement）**：2.5 - 4 秒
- **差（Poor）**：> 4 秒

### 6.4 测量方法

#### Chrome DevTools 测量

1. 打开 DevTools → **Performance** 面板
2. 勾选 **Web Vitals** 录制选项
3. 刷新录制页面加载过程
4. 在火焰图时间轴上查找 **LCP** 标记

#### Lighthouse 测量

1. 打开 DevTools → **Lighthouse** 面板
2. 选择 **Performance** 类别
3. 点击 **Analyze page load**
4. 查看报告中 LCP 数值与优化建议

#### JavaScript API 测量

```javascript
// 使用 PerformanceObserver 监听 LCP
new PerformanceObserver((entryList) => {
  const entries = entryList.getEntries();
  const lastEntry = entries[entries.length - 1]; // 取最后一次（最终 LCP）
  console.log('LCP:', lastEntry.startTime);
  console.log('LCP 元素:', lastEntry.element);
  console.log('LCP URL:', lastEntry.url); // 如果是图片
  console.log('LCP 加载时间:', lastEntry.loadTime);
}).observe({ type: 'largest-contentful-paint', buffered: true });

// 使用 web-vitals 库（推荐）
import { onLCP } from 'web-vitals';

onLCP((metric) => {
  console.log('LCP:', metric.value);
  console.log('评分:', metric.rating);  // 'good' | 'needs-improvement' | 'poor'
  console.log('详细信息:', metric.entries);
});
```

### 6.5 影响因素分析

LCP 受以下四个时间阶段影响：

```
LCP 总时间 = TTFB + 资源加载延迟 + 资源加载时间 + 渲染延迟

┌───────────────────────────────────────────────────────────────┐
│ TTFB            │ 加载延迟        │ 资源加载     │ 渲染延迟   │
│ (首字节时间)     │ (发现资源耗时)   │ (传输耗时)   │ (渲染耗时) │
└───────────────────────────────────────────────────────────────┘
```

| 阶段 | 影响因素 | 占比（典型） |
|------|----------|-------------|
| **TTFB** | 服务器响应速度、CDN 配置、重定向 | 20-30% |
| **资源加载延迟** | 关键资源优先级、预加载配置 | 10-20% |
| **资源加载时间** | 资源体积、压缩、网络带宽 | 30-50% |
| **渲染延迟** | CSS 阻塞、JS 执行、客户端渲染 | 10-30% |

### 6.6 优化策略

#### 策略一：优化 TTFB

```javascript
// 服务端优化示例（Node.js）
// ❌ 未优化：串行数据库查询
app.get('/page', async (req, res) => {
  const user = await db.getUser(req.userId);
  const data = await db.getData(user.id);
  const config = await db.getConfig();
  res.render('page', { user, data, config });
});

// ✅ 优化：并行查询 + 缓存
const cache = new Map();
app.get('/page', async (req, res) => {
  const [user, data, config] = await Promise.all([
    cache.has('user') ? cache.get('user') : db.getUser(req.userId),
    db.getData(req.userId),
    cache.has('config') ? cache.get('config') : db.getConfig(),
  ]);
  res.setHeader('Cache-Control', 'public, max-age=60, s-maxage=300');
  res.render('page', { user, data, config });
});
```

其他 TTFB 优化手段：
- 使用 CDN 就近分发
- 启用 HTTP/2 或 HTTP/3
- 减少 重定向次数
- 使用边缘计算（Edge Functions）
- 配置 Service Worker 缓存

#### 策略二：设置资源优先级与预加载

```html
<!-- 预加载 LCP 图片（最有效的方式之一） -->
<link rel="preload" as="image" href="/hero-image.webp" fetchpriority="high" />

<!-- 使用 fetchpriority 属性提升优先级 -->
<img src="/hero-image.webp" fetchpriority="high" alt="Hero image" />

<!-- 降低非关键资源优先级 -->
<img src="/low-priority-image.png" fetchpriority="low" loading="lazy" alt="Decoration" />
```

#### 策略三：优化渲染路径

```html
<head>
  <!-- ✅ 内联关键 CSS，避免阻塞渲染 -->
  <style>
    /* 首屏关键样式 */
    .hero { width: 100%; height: 60vh; background: #f0f0f0; }
    .hero-image { width: 100%; height: 100%; object-fit: cover; }
  </style>

  <!-- ✅ 为 LCP 图片设置明确尺寸，避免布局偏移 -->
  <link rel="preload" as="image" href="/hero.webp" />

  <!-- ✅ 非关键 CSS 异步加载 -->
  <link rel="preload" href="/styles/main.css" as="style"
        onload="this.onload=null;this.rel='stylesheet'" />
</head>
<body>
  <!-- ✅ LCP 图片：明确宽高 + fetchpriority + 现代 图片格式 -->
  <img src="/hero.webp"
       width="1200" height="600"
       fetchpriority="high"
       alt="Hero"
       style="aspect-ratio: 2/1" />

  <!-- ✅ 使用响应式图片，避免加载过大图片 -->
  <img srcset="/hero-480.webp 480w,
               /hero-800.webp 800w,
               /hero-1200.webp 1200w"
       sizes="100vw"
       width="1200" height="600"
       fetchpriority="high"
       alt="Hero" />
</body>
```

#### 策略四：SSR / SSG 替代 CSR

```javascript
// ❌ CSR：LCP 依赖 JS 执行后才渲染内容
// index.html → 下载 JS → 执行 JS → 请求数据 → 渲染 LCP

// ✅ SSR（Next.js 示例）：服务端直接输出 HTML
export async function getServerSideProps() {
  const data = await fetchHeroData();
  return { props: { heroData: data } };
}

// ✅ SSG（Next.js 示例）：构建时生成静态页面
export async function getStaticProps() {
  const data = await fetchHeroData();
  return {
    props: { heroData: data },
    revalidate: 3600, // ISR: 每小时重新生成
  };
}
```

---

## 七、CLS — Cumulative Layout Shift

### 7.1 定义

**CLS（累积布局偏移）** 衡量的是页面整个生命周期中所有意外布局偏移的总和。它反映了页面的**视觉稳定性**——内容是否会在用户阅读或交互时突然移动。

### 7.2 布局偏移的计算方式

```
布局偏移分数 = 影响比例(Impact Fraction) × 距离比例(Distance Fraction)

影响比例 = 不稳定元素在视口中占用的面积 ∩ 联合面积 / 视口面积
距离比例 = 不稳定元素在视口中移动的最大距离 / 视口尺寸

示例：
┌─────────────────────────┐
│  ┌─────────────┐        │  偏移前
│  │   元素 A     │        │
│  └─────────────┘        │
│                         │
└─────────────────────────┘

┌─────────────────────────┐
│                         │  偏移后：元素下移了 80px
│       ┌─────────────┐  │
│       │   元素 A     │  │
│       └─────────────┘  │
└─────────────────────────┘

假设视口高度 800px，元素高度 200px，下移 80px：
- 影响比例 = (200 + 80) / 800 = 0.35（联合高度占视口比）
- 距离比例 = 80 / 800 = 0.10
- 本次偏移分数 = 0.35 × 0.10 = 0.035
```

### 7.3 行业标准值

```
     0         0.1          0.25
─────┣━━━━━━━━━╋━━━━━━━━━━━╋────────▶
      ┃  良好   ┃  需改进    ┃   差
      ┃ (Good)  ┃ (Needs    ┃ (Poor)
      ┃         ┃ Improve)  ┃
    ≤ 0.1    0.1 - 0.25   > 0.25
```

- **良好（Good）**：≤ 0.1
- **需改进（Needs Improvement）**：0.1 - 0.25
- **差（Poor）**：> 0.25

### 7.4 测量方法

```javascript
// 使用 PerformanceObserver 监听布局偏移
new PerformanceObserver((entryList) => {
  for (const entry of entryList.getEntries()) {
    // 仅统计非用户交互引起的偏移
    if (!entry.hadRecentInput) {
      console.log('布局偏移:', entry.value);
      console.log('偏移元素:', entry.sources?.map(s => s.node));
    }
  }
}).observe({ type: 'layout-shift', buffered: true });

// 使用 web-vitals 库
import { onCLS } from 'web-vitals';

onCLS((metric) => {
  console.log('CLS:', metric.value);
  console.log('评分:', metric.rating);
});
```

#### DevTools Layout Shift Regions 可视化

1. 打开 DevTools → **Rendering** 面板（`Ctrl + Shift + P` → 输入 "Rendering"）
2. 勾选 **Layout Shift Regions**
3. 布局偏移区域会以蓝色高亮显示

### 7.5 布局偏移常见原因

| 原因 | 场景 | CLS 贡献 |
|------|------|----------|
| **无尺寸的图片/视频** | 图片加载后撑开容器 | ⭐⭐⭐⭐⭐ |
| **动态注入内容** | 广告、推荐组件插入 | ⭐⭐⭐⭐⭐ |
| **Web 字体加载闪烁** | FOUT/FOIT 现象 | ⭐⭐⭐⭐ |
| **异步 DOM 更新** | 延迟加载的组件 | ⭐⭐⭐ |
| **缺少骨架屏** | 内容加载后撑开布局 | ⭐⭐⭐ |
| **动态 CSS** | 样式延迟应用 | ⭐⭐ |

### 7.6 优化技术

#### 技术一：为图片和视频设置明确尺寸

```html
<!-- ❌ 优化前：无尺寸，加载后导致布局偏移 -->
<img src="/product.jpg" alt="Product">

<!-- ✅ 优化后：设置宽高或 aspect-ratio -->
<img src="/product.jpg" alt="Product" width="800" height="600">

<!-- ✅ 使用 CSS aspect-ratio（更灵活） -->
<img src="/product.jpg" alt="Product"
     style="aspect-ratio: 4/3; width: 100%; height: auto;">

<!-- ✅ 响应式图片 + 尺寸 -->
<img srcset="/product-400.jpg 400w,
             /product-800.jpg 800w"
     sizes="(max-width: 600px) 100vw, 50vw"
     width="800" height="600"
     alt="Product">
```

```css
/* ✅ 视频元素同样需要设置尺寸 */
.video-container {
  aspect-ratio: 16 / 9;
  width: 100%;
}

.video-container video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
```

#### 技术二：预留动态内容空间

```html
<!-- ❌ 优化前：广告位无预留空间，加载后推下内容 -->
<div id="ad-container"></div>
<script>
  // 广告加载后 DOM 插入，导致下方内容下移
  loadAd().then(ad => {
    document.getElementById('ad-container').innerHTML = ad;
  });
</script>

<!-- ✅ 优化后：预留广告位高度 -->
<div id="ad-container" style="min-height: 250px;">
  <!-- 广告加载前显示占位 -->
  <div class="ad-placeholder">广告位</div>
</div>
```

#### 技术三：使用骨架屏

```html
<!-- ✅ 骨架屏占位 -->
<div class="card-skeleton" aria-hidden="true">
  <div class="skeleton-image"></div>
  <div class="skeleton-title"></div>
  <div class="skeleton-text"></div>
  <div class="skeleton-text short"></div>
</div>
```

```css
.skeleton-image,
.skeleton-title,
.skeleton-text {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.skeleton-image {
  width: 100%;
  aspect-ratio: 16 / 9;  /* 关键：与实际图片比例一致 */
}

.skeleton-title {
  height: 24px;
  margin-top: 12px;
  width: 60%;
}

.skeleton-text {
  height: 16px;
  margin-top: 8px;
  width: 100%;
}

.skeleton-text.short {
  width: 40%;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

#### 技术四：优化 Web 字体加载

```css
/* ❌ 字体未加载时隐藏文字（FOIT），加载后突然出现导致偏移 */

/* ✅ 方案 1：font-display: swap — 立即显示后备字体 */
@font-face {
  font-family: 'MyFont';
  src: url('/fonts/MyFont.woff2') format('woff2');
  font-display: swap;  /* 先用系统字体，字体加载完后替换 */
}

/* ✅ 方案 2：使用 size-adjust 匹配后备字体宽度 */
@font-face {
  font-family: 'MyFont-fallback';
  src: local('Arial');
  size-adjust: 105.2%;  /* 调整后备字体大小，减少偏移 */
  ascent-override: 98%;
  descent-override: 22%;
  line-gap-override: 0;
}

body {
  font-family: 'MyFont', 'MyFont-fallback', sans-serif;
}
```

```html
<!-- ✅ 预加载关键字体，减少字体加载延迟 -->
<link rel="preload" href="/fonts/MyFont.woff2" as="font" type="font/woff2" crossorigin />
```

#### 技术五：使用 CSS contain 属性

```css
/* ✅ 限制元素布局影响范围 */
.ad-widget {
  contain: layout;  /* 元素内部的布局变化不影响外部 */
  /* 或更强的约束 */
  contain: strict;  /* 等同于 contain: size layout style paint */
}

.sidebar {
  contain: layout style;
}
```

---

## 八、INP — Interaction to Next Paint

### 8.1 定义

**INP（交互到下次绘制）** 衡量的是用户与页面交互后到页面下一次视觉更新（绘制）的延迟时间。它反映了页面的**交互响应性**。

> INP 于 2024 年 3 月正式取代 FID（First Input Delay）成为 Core Web Vitals 指标。

### 8.2 INP 与 FID 的区别

| 维度 | FID | INP |
|------|-----|-----|
| **测量范围** | 仅首次交互 | 全部交互 |
| **测量内容** | 仅输入延迟 | 输入延迟 + 处理时间 + 呈现延迟 |
| **计算方式** | 单次值 | 全部交互的最差值（或 98 百分位） |
| **代表性** | 仅反映首次点击/按键 | 反映整个页面生命周期的响应性 |
| **状态** | 已被 INP 取代 | 当前 Core Web Vitals 指标 |

```
FID 仅测量：               INP 测量完整流程：
┌──────────┐              ┌──────────┬──────────┬──────────┐
│ 输入延迟  │              │ 输入延迟  │  处理时间  │ 呈现延迟  │
│ (Input    │              │ (Input   │ (Process  │ (Present  │
│  Delay)   │              │  Delay)  │  Time)   │  Delay)   │
└──────────┘              └──────────┴──────────┴──────────┘
                            │                         │
用户点击 ─────────────────────▶ 事件回调执行 ◀────────────▶ 下一帧绘制
```

### 8.3 行业标准值

```
      0ms         200ms         500ms
──────┣━━━━━━━━━━╋━━━━━━━━━━━━━╋────────▶
       ┃   良好   ┃   需改进     ┃    差
       ┃  (Good)  ┃   (Needs    ┃  (Poor)
       ┃          ┃ Improvement)┃
     ≤ 200ms   200-500ms     > 500ms
```

- **良好（Good）**：≤ 200ms
- **需改进（Needs Improvement）**：200 - 500ms
- **差（Poor）**：> 500ms

### 8.4 测量方法

```javascript
// 使用 PerformanceObserver 监听 INP
new PerformanceObserver((entryList) => {
  for (const entry of entryList.getEntries()) {
    if (entry.interactionId) {
      const inp = entry.duration; // 包含输入延迟 + 处理 + 呈现
      console.log('交互类型:', entry.name);     // 'pointerdown' / 'keydown' 等
      console.log('INP:', inp);
    }
  }
}).observe({ type: 'event', buffered: true, durationThreshold: 16 });

// 使用 web-vitals 库
import { onINP } from 'web-vitals';

onINP((metric) => {
  console.log('INP:', metric.value);
  console.log('评分:', metric.rating);
  console.log('交互类型:', metric.entries[0]?.name);
});
```

#### Chrome DevTools 识别 INP

1. 打开 Performance 面板，录制用户交互
2. 在 **Interactions** 轨道查看交互标记
3. 检查 Main 线程中交互回调的执行时长
4. 确认回调完成后是否及时触发了 Paint

<!-- 截图：INP 分析 -->
> 📷 截图参考：`assets/performance-08-inp-analysis.png` — Performance 面板中的 INP 分析

### 8.5 交互延迟的常见原因

| 原因 | 机制 | 典型场景 |
|------|------|----------|
| **主线程被长任务阻塞** | 事件回调必须等长任务结束 | 大量数据计算、复杂 DOM 操作 |
| **事件处理器过重** | 回调执行时间过长 | 复杂表单验证、大量状态更新 |
| **强制同步布局** | 回调中读写交替触发重排 | 读取 offsetHeight 后修改样式 |
| **过多事件监听** | 事件分发耗时长 | 未使用事件委托 |
| **第三方脚本** | 主线程被第三方代码占用 | 分析工具、广告 SDK |
| **渲染更新延迟** | 回调后未及时触发绘制 | requestAnimationFrame 使用不当 |

### 8.6 优化策略

#### 策略一：优化事件处理器

```javascript
// ❌ 优化前：搜索输入每次按键都执行重操作
searchInput.addEventListener('input', (e) => {
  const results = heavySearch(e.target.value);  // 每次按键都执行搜索
  renderResults(results);  // 每次都重新渲染
});

// ✅ 优化后：防抖 + requestAnimationFrame
searchInput.addEventListener('input', (e) => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    const results = heavySearch(e.target.value);
    requestAnimationFrame(() => renderResults(results));
  }, 300);
});
```

#### 策略二：减少主线程阻塞

```javascript
// ❌ 优化前：点击排序在主线程处理 10000 条数据
sortButton.addEventListener('click', () => {
  // 10000 条数据排序可能耗时 200ms+，阻塞主线程
  const sorted = data.sort((a, b) => a.name.localeCompare(b.name));
  renderTable(sorted);
});

// ✅ 优化后：使用 Web Worker 处理数据
const sortWorker = new Worker('sort-worker.js');

sortButton.addEventListener('click', () => {
  sortWorker.postMessage({ data, field: 'name' });
  // 主线程空闲，可响应用户交互
});

sortWorker.onmessage = (e) => {
  renderTable(e.data);  // 排序完成后更新 UI
});
```

#### 策略三：使用 scheduler.yield() 让出主线程

```javascript
// ❌ 长任务阻塞主线程，后续交互必须等待
function handleButtonClick() {
  validateForm();        // 50ms
  processData();        // 150ms
  updateUI();           // 30ms
  // 总计 230ms，INP 差
}

// ✅ 在关键点让出主线程，确保及时响应
async function handleButtonClick() {
  validateForm();              // 50ms
  await scheduler.yield();     // 让出主线程，处理待处理的交互/渲染
  processData();              // 150ms
  await scheduler.yield();     // 再次让出
  updateUI();                  // 30ms
  // 用户感知的 INP 显著降低
}
```

> `scheduler.yield()` 是较新的 API，兼容性有限。替代方案：
```javascript
// 兼容性更好的让出方式
function yieldToMain() {
  return new Promise(resolve => {
    setTimeout(resolve, 0);
  });
}
```

#### 策略四：使用事件委托减少监听器

```javascript
// ❌ 每个按钮单独监听（1000 个按钮 = 1000 个监听器）
document.querySelectorAll('.action-btn').forEach(btn => {
  btn.addEventListener('click', handleClick);
});

// ✅ 事件委托：仅一个监听器
document.querySelector('.btn-container').addEventListener('click', (e) => {
  const btn = e.target.closest('.action-btn');
  if (btn) {
    handleClick({ target: btn, currentTarget: btn });
  }
});
```

#### 策略五：拆分复杂回调

```javascript
// ❌ 点击后一次性渲染所有组件
tabContainer.addEventListener('click', async (e) => {
  const tab = e.target.closest('.tab');
  if (!tab) return;

  // 一次性加载并渲染所有面板内容
  const data1 = await fetchPanel1Data();
  renderPanel1(data1);
  const data2 = await fetchPanel2Data();
  renderPanel2(data2);
  const data3 = await fetchPanel3Data();
  renderPanel3(data3);
  // 用户等待所有面板渲染完毕才能看到任何反馈
});

// ✅ 先渲染最关键内容，其余延迟处理
tabContainer.addEventListener('click', async (e) => {
  const tab = e.target.closest('.tab');
  if (!tab) return;

  // 优先渲染首屏面板
  const criticalData = await fetchCriticalPanelData();
  renderCriticalPanel(criticalData);  // 快速响应

  // 其余面板空闲时加载
  requestIdleCallback(async () => {
    const secondaryData = await fetchSecondaryPanelData();
    renderSecondaryPanel(secondaryData);
  });
});
```

---

# 第三部分：实战案例分析

## 案例一：电商首页 LCP 优化

### 问题描述

某电商平台首页 LCP 为 **5.2 秒**（差），LCP 元素为首屏 Hero Banner 图片。

### 诊断过程

#### Step 1：Performance 面板录制

1. 设置 Network: Fast 3G，CPU: 6x slowdown
2. 刷新录制页面加载
3. 在时间轴定位 LCP 标记

#### Step 2：分析 LCP 时间分解

```
LCP 总时间 = 5200ms

TTFB:           800ms   (15%)  ← 服务端渲染较慢
资源加载延迟:    1200ms  (23%)  ← 图片发现较晚
资源加载时间:    2800ms  (54%)  ← 图片体积过大
渲染延迟:        400ms   (8%)   ← CSS 阻塞渲染

主要瓶颈：资源加载时间（54%）
```

#### Step 3：火焰图分析

```
Network 瀑布图分析：
  HTML          ████████████                                800ms (TTFB)
  CSS (render-blocking)  ───────────████████████             600ms
  JS (render-blocking)   ────────────────████████████████    900ms
  Hero Banner           ────────────────────────████████████████████████  2800ms
                                                                                  ↑
                                                                      LCP: 5200ms
```

**发现**：
1. Hero 图片未被预加载，需等 CSS/JS 解析后才发现
2. Hero 图片为 2MB JPEG，体积过大
3. CSS 和 JS 阻塞了图片的渲染

### 优化措施

| 措施 | 实施内容 | 预期提升 |
|------|----------|----------|
| 预加载 Hero 图片 | 添加 `<link rel="preload">` | -1200ms |
| 图片格式优化 | JPEG → WebP，质量 85 | -1400ms |
| 响应式图片 | 按设备提供不同尺寸 | -400ms（移动端） |
| 内联关键 CSS | 首屏样式内联 | -300ms |
| JS 异步加载 | 非关键 JS 加 `defer` | -200ms |

#### 实施代码

```html
<head>
  <!-- ✅ 预加载 Hero 图片 -->
  <link rel="preload" as="image" href="/hero-banner.webp"
        fetchpriority="high" />

  <!-- ✅ 内联首屏关键 CSS -->
  <style>
    .hero-banner {
      width: 100%;
      aspect-ratio: 21/9;
      background: #f5f5f5;
    }
    .hero-banner img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  </style>

  <!-- ✅ 非关键 CSS 异步加载 -->
  <link rel="preload" href="/css/main.css" as="style"
        onload="this.onload=null;this.rel='stylesheet'" />

  <!-- ✅ 非关键 JS 延迟加载 -->
  <script src="/js/analytics.js" defer></script>
  <script src="/js/recommendations.js" defer></script>
</head>
<body>
  <!-- ✅ 响应式 WebP 图片 + 明确尺寸 + 高优先级 -->
  <picture>
    <source media="(max-width: 768px)"
            srcset="/hero-banner-480.webp"
            type="image/webp" />
    <source media="(max-width: 1200px)"
            srcset="/hero-banner-800.webp"
            type="image/webp" />
    <img src="/hero-banner-1200.webp"
         alt="Summer Sale"
         width="1200" height="514"
         fetchpriority="high"
         loading="eager" />
  </picture>
</body>
```

### 优化结果

```
优化前：LCP = 5200ms (差)
优化后：LCP = 1600ms (良好)

TTFB:           800ms → 600ms    (CDN 优化)
资源加载延迟:    1200ms → 0ms     (preload)
资源加载时间:    2800ms → 800ms   (WebP + 响应式)
渲染延迟:        400ms → 200ms   (内联关键 CSS)

总计提升：3600ms（-69%）
```

---

## 案例二：内容资讯站 CLS 优化

### 问题描述

某新闻资讯站 CLS 为 **0.38**（差），用户反馈页面内容经常"跳动"。

### 诊断过程

#### Step 1：开启 Layout Shift Regions

1. `Ctrl + Shift + P` → 输入 "Rendering"
2. 勾选 **Layout Shift Regions**
3. 刷新页面，观察蓝色高亮区域

#### Step 2：使用 Performance 录制

1. 录制页面加载过程
2. 在 Layout Shift 轨道查看每次偏移

#### Step 3：识别偏移来源

```
Layout Shift 分析：

偏移 #1：CLS = 0.15
  来源：<img class="article-image"> — 图片无尺寸，加载后撑开
  影响：文章区域下移 120px

偏移 #2：CLS = 0.12
  来源：<div id="ad-slot"> — 广告异步插入
  影响：侧边栏下移，主内容区压缩

偏移 #3：CLS = 0.08
  来源：h1 标题 — Web 字体加载后文字宽度变化
  影响：标题行数变化导致下方内容偏移

偏移 #4：CLS = 0.03
  来源：<div class="cookie-banner"> — Cookie 横幅从顶部插入
  影响：全部内容下移 60px

总计 CLS = 0.38
```

### 优化措施

```html
<!-- ✅ 措施1：为图片设置明确尺寸 -->
<img class="article-image"
     src="/article-photo.webp"
     alt="Article photo"
     width="800" height="450"
     style="aspect-ratio: 16/9; width: 100%; height: auto;"
     loading="lazy" />

<!-- ✅ 措施2：广告位预留空间 -->
<div class="ad-slot" style="min-height: 250px;">
  <div class="ad-placeholder" aria-hidden="true"></div>
</div>

<!-- ✅ 措施3：Cookie 横幅固定定位（不占用文档流） -->
<div class="cookie-banner" style="position: fixed; bottom: 0; left: 0; right: 0; z-index: 1000;">
  <!-- Cookie 内容 -->
</div>
```

```css
/* ✅ 措施4：字体优化 — size-adjust 匹配后备字体 */
@font-face {
  font-family: 'NewsTitle';
  src: url('/fonts/NewsTitle.woff2') format('woff2');
  font-display: swap;
}

@font-face {
  font-family: 'NewsTitle-fallback';
  src: local('Georgia');
  size-adjust: 108.5%;
  ascent-override: 92%;
  descent-override: 20%;
}

h1, h2 {
  font-family: 'NewsTitle', 'NewsTitle-fallback', serif;
}

/* ✅ 措施5：CSS contain 限制布局影响 */
.ad-slot {
  contain: layout style;
  min-height: 250px;
}
```

### 优化结果

```
优化前：CLS = 0.38 (差)
优化后：CLS = 0.04 (良好)

偏移 #1：0.15 → 0.00  (图片设置尺寸)
偏移 #2：0.12 → 0.02  (广告预留空间，含微小偏移)
偏移 #3：0.08 → 0.01  (font-display: swap + size-adjust)
偏移 #4：0.03 → 0.00  (Cookie 固定定位)
新增偏移：0.01         (字体 swap 过渡)

总计提升：0.34 (-89%)
```

---

## 案例三：SPA 应用 INP 优化

### 问题描述

某 React 单页应用 INP 为 **680ms**（差），用户点击筛选按钮后页面明显卡顿。

### 诊断过程

#### Step 1：Performance 录制交互

1. 点击 🔴 开始录制
2. 点击筛选按钮
3. 等待页面更新完成
4. 停止录制

#### Step 2：分析 Main 线程火焰图

```
Main 线程（点击筛选按钮后）：

│ Task ──────────────────────────────────────────────────────────── 680ms
│ ┌──────────────────────────────────────────────────────────────┐
│ │ Event: click                                                  │
│ │ ┌──────────────────────┐                                      │
│ │ │ filterData()         │  180ms                               │
│ │ └──────────────────────┘                                      │
│ │ ┌──────────────────────────────────────────────┐              │
│ │ │ React reconcile + commit                      │  420ms      │
│ │ │ ┌──────────────────────────────────────────┐ │              │
│ │ │ │ renderList (500 items)                    │ │              │
│ │ │ │ ┌────────────────────┐ ┌───────────────┐ │ │              │
│ │ │ │ │ createElement ×500 │ │ DOM.append     │ │ │              │
│ │ │ │ └────────────────────┘ └───────────────┘ │ │              │
│ │ │ └──────────────────────────────────────────┘ │              │
│ │ └──────────────────────────────────────────────┘              │
│ │ ┌────────────────────────┐                                    │
│ │ │ Style + Layout + Paint │  80ms                              │
│ │ └────────────────────────┘                                    │
│ └──────────────────────────────────────────────────────────────┘
```

**瓶颈识别**：
1. `filterData()` 数据筛选耗时 180ms
2. React 渲染 500 个列表项耗时 420ms（含 DOM 操作）
3. 渲染更新 80ms
4. 总计 680ms，远超 200ms 目标

### 优化措施

#### 措施一：数据筛选移入 Web Worker

```javascript
// filter-worker.js
self.onmessage = (e) => {
  const { data, filters } = e.data;
  const filtered = data.filter(item => {
    return filters.every(filter => {
      const value = item[filter.field];
      if (filter.operator === 'eq') return value === filter.value;
      if (filter.operator === 'contains') return value.includes(filter.value);
      if (filter.operator === 'gt') return value > filter.value;
      return true;
    });
  });
  self.postMessage(filtered);
};

// main.js
const filterWorker = new Worker('filter-worker.js');

function handleFilter(filters) {
  filterWorker.postMessage({ data: allData, filters });
}

filterWorker.onmessage = (e) => {
  setFilteredData(e.data);  // Worker 返回后更新状态
};
```

#### 措施二：虚拟列表减少 DOM 操作

```javascript
// ✅ 使用 react-window 替代全量渲染
import { FixedSizeList } from 'react-window';

function FilterableList({ items }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      <ItemCard item={items[index]} />
    </div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={80}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
}
```

#### 措施三：使用 startTransition 降低优先级

```javascript
import { useTransition, useState } from 'react';

function ProductPage({ products }) {
  const [filter, setFilter] = useState('');
  const [isPending, startTransition] = useTransition();

  const handleFilterChange = (value) => {
    // 立即更新输入框（高优先级）
    setFilter(value);

    // 延迟更新列表（低优先级，不阻塞输入）
    startTransition(() => {
      setFilteredProducts(applyFilter(products, value));
    });
  };

  return (
    <div>
      <SearchInput value={filter} onChange={handleFilterChange} />
      {isPending && <Spinner />}
      <ProductList items={filteredProducts} />
    </div>
  );
}
```

### 优化结果

```
优化前：INP = 680ms (差)

优化后：
  - 数据筛选：180ms → 0ms（Worker 中执行，不阻塞主线程）
  - React 渲染：420ms → 30ms（虚拟列表，仅渲染可见项）
  - 样式/布局/绘制：80ms → 20ms（DOM 节点从 500 减少到 ~8）
  - 主线程总耗时：~50ms

INP = 50ms (良好)

总计提升：630ms (-93%)
```

---

# 第四部分：性能测试环境配置与持续优化

## 九、性能测试环境配置建议

### 9.1 本地测试环境

#### Chrome DevTools 配置

```
推荐配置：
┌─────────────────────────────────────────────────┐
│ Network Throttling                               │
│   ├─ 桌面端：不节流 或 "Fast 3G"                   │
│   └─ 移动端：Slow 3G / Fast 3G                    │
│                                                   │
│ CPU Throttling                                    │
│   ├─ 桌面端：No throttling                        │
│   └─ 模拟移动端：6x slowdown                      │
│                                                   │
│ 缓存                                              │
│   ├─ 首次加载测试：Disable cache ✅                │
│   └─ 返访测试：保持缓存                            │
│                                                   │
│ 录制选项                                          │
│   ├─ Screenshots ✅                               │
│   ├─ Memory ❌（除非分析内存问题）                  │
│   └─ Web Vitals ✅                                │
└─────────────────────────────────────────────────┘
```

#### 推荐的 Chrome Flag 设置

在地址栏输入 `chrome://flags`：

| Flag | 设置 | 用途 |
|------|------|------|
| `#enable-quic` | Enabled | 启用 HTTP/3 |
| `#autofill-overlap-scrollbar` | Default | 确保渲染一致 |

### 9.2 模拟真实用户设备

```bash
# 使用 Chrome 的 --cpu-throttling 启动参数
chrome --cpu-throttling=6 --user-data-dir=/tmp/chrome-perf

# 使用 Lighthouse CI 的预设配置
# desktop 配置
{
  "preset": "desktop",
  "throttling": {
    "rttMs": 0,
    "throughputKbps": 0,
    "cpuSlowdownMultiplier": 1
  }
}

# mobile 配置
{
  "preset": "mobile",
  "throttling": {
    "rttMs": 150,
    "throughputKbps": 1638.4,
    "cpuSlowdownMultiplier": 4
  }
}
```

### 9.3 自动化性能测试

#### Lighthouse CI 配置

```javascript
// lighthouserc.js
module.exports = {
  ci: {
    collect: {
      // 测试页面
      url: ['http://localhost:3000/', 'http://localhost:3000/products'],
      // 运行次数（取中位数）
      numberOfRuns: 5,
      // 预设
      preset: 'desktop',
    },
    assert: {
      // 性能断言
      assertions: {
        'categories:performance': ['warn', { minScore: 0.9 }],
        'metrics:lcp': ['error', { maxNumericValue: 2500 }],
        'metrics:cls': ['error', { maxNumericValue: 0.1 }],
        'metrics:inp': ['error', { maxNumericValue: 200 }],
        'resource-summary:script:size': ['warn', { maxNumericValue: 300000 }],
        'resource-summary:stylesheet:size': ['warn', { maxNumericValue: 50000 }],
      },
    },
    upload: {
      target: 'lhci',
      serverBaseUrl: 'https://lhci.example.com',
    },
  },
};
```

#### WebPageTest API

```javascript
// 使用 WebPageTest API 进行真实设备测试
const WebPageTest = require('webpagetest');

const wpt = new WebPageTest('www.webpagetest.org', 'YOUR_API_KEY');

// 移动端测试
wpt.runTest('https://example.com', {
  location: 'Dulles_MotoG5:Motorola G (gen 5)',  // 真实移动设备
  connectivity: '3G',
  runs: 3,
  firstViewOnly: false,
  lighthouse: true,
}, (err, data) => {
  console.log('测试ID:', data.data.testId);
  console.log('结果URL:', data.data.summary);
});
```

---

## 十、性能监控与持续优化方法论

### 10.1 建立 RUM（Real User Monitoring）监控

```javascript
// 使用 web-vitals 库采集真实用户数据
import { onLCP, onCLS, onINP, onFCP, onTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  const body = JSON.stringify({
    name: metric.name,
    value: metric.value,
    rating: metric.rating,
    delta: metric.delta,
    id: metric.id,
    url: window.location.href,
    userAgent: navigator.userAgent,
    timestamp: Date.now(),
  });

  // 使用 sendBeacon 确保页面卸载时也能发送
  if (navigator.sendBeacon) {
    navigator.sendBeacon('/api/vitals', body);
  } else {
    fetch('/api/vitals', { body, method: 'POST', keepalive: true });
  }
}

// 注册所有核心指标监听
onLCP(sendToAnalytics);
onCLS(sendToAnalytics);
onINP(sendToAnalytics);
onFCP(sendToAnalytics);
onTTFB(sendToAnalytics);
```

### 10.2 性能预算（Performance Budget）

```javascript
// performance-budget.config.js
module.exports = {
  // 资源体积预算
  resourceSizes: [
    { path: '**/*.js',     maxSize: '200 KiB' },
    { path: '**/*.css',    maxSize: '50 KiB'  },
    { path: '**/*.woff2',  maxSize: '100 KiB' },
    { path: '**/*.webp',   maxSize: '200 KiB' },
  ],

  // 性能指标预算
  metrics: {
    lcp:   { target: 2500,  warning: 2000  },
    cls:   { target: 0.1,   warning: 0.05  },
    inp:   { target: 200,   warning: 150   },
    fcp:   { target: 1800,  warning: 1500  },
    ttfb:  { target: 800,   warning: 500   },
    tti:   { target: 3800,  warning: 3000  },
  },

  // 总资源预算
  totalSize: '1 MiB',
};
```

### 10.3 持续优化工作流

```
┌──────────────────────────────────────────────────────────────┐
│                    性能优化闭环                                │
│                                                              │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌────────┐ │
│  │  监控    │────▶│  诊断    │────▶│  优化    │────▶│  验证  │ │
│  │ Monitor │     │ Diagnose│     │ Optimize │     │ Verify │ │
│  └────▲────┘     └─────────┘     └─────────┘     └────┬───┘ │
│       │                                                 │     │
│       └─────────────────────────────────────────────────┘     │
│                      回归监控                                  │
└──────────────────────────────────────────────────────────────┘

1. 监控：RUM + Synthesis 监控，设置告警阈值
2. 诊断：Performance 面板 + Lighthouse 分析瓶颈
3. 优化：按优先级实施优化措施
4. 验证：A/B 测试 + Lighthouse CI 回归测试
5. 回归：持续监控，防止性能退化
```

#### 监控告警配置示例

```yaml
# 告警规则示例
alerts:
  - name: LCP 退化
    condition: p75_lcp > 3000
    duration: 5m
    action: notify Slack #performance-channel

  - name: CLS 异常
    condition: p75_cls > 0.15
    duration: 10m
    action: notify Slack #performance-channel

  - name: INP 变差
    condition: p75_inp > 350
    duration: 15m
    action: notify Slack #performance-channel
    escalation: create JIRA ticket

  - name: 资源体积超预算
    condition: total_js_size > 250KB
    action: block deployment
```

### 10.4 性能优化优先级矩阵

| 优化措施 | LCP 影响 | CLS 影响 | INP 影响 | 实施难度 | 优先级 |
|----------|----------|----------|----------|----------|--------|
| 预加载关键资源 | ⭐⭐⭐⭐⭐ | — | — | 低 | **P0** |
| 图片尺寸/格式 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | — | 低 | **P0** |
| 代码拆分 | ⭐⭐⭐ | — | ⭐⭐⭐ | 中 | **P0** |
| 字体优化 | ⭐⭐ | ⭐⭐⭐ | — | 低 | **P1** |
| 虚拟列表 | — | — | ⭐⭐⭐⭐⭐ | 中 | **P1** |
| Web Workers | — | — | ⭐⭐⭐⭐⭐ | 高 | **P1** |
| 预留广告空间 | — | ⭐⭐⭐⭐⭐ | — | 低 | **P1** |
| SSR/SSG | ⭐⭐⭐⭐⭐ | — | — | 高 | **P2** |
| CSS contain | — | ⭐⭐⭐ | — | 低 | **P2** |
| scheduler.yield | — | — | ⭐⭐⭐⭐ | 低 | **P2** |

> **P0**：立即实施，投入产出比最高
> **P1**：短期规划，影响显著
> **P2**：中期规划，需要一定工程量

---

# 附录

## A. Core Web Vitals 指标速查表

| 指标 | 全称 | 测量内容 | 良好 | 需改进 | 差 |
|------|------|----------|------|--------|-----|
| **LCP** | Largest Contentful Paint | 最大内容绘制 | ≤2.5s | 2.5-4s | >4s |
| **CLS** | Cumulative Layout Shift | 累积布局偏移 | ≤0.1 | 0.1-0.25 | >0.25 |
| **INP** | Interaction to Next Paint | 交互到下次绘制 | ≤200ms | 200-500ms | >500ms |
| FCP | First Contentful Paint | 首次内容绘制 | ≤1.8s | 1.8-3s | >3s |
| TTFB | Time to First Byte | 首字节时间 | ≤800ms | 800-1800ms | >1800ms |

## B. Chrome DevTools 快捷键

| 快捷键 | 功能 |
|--------|------|
| `F12` / `Ctrl+Shift+I` | 打开 DevTools |
| `Ctrl+Shift+E` | 打开 Performance 面板 |
| `Ctrl+E` | 开始/停止 Performance 录制 |
| `Ctrl+Shift+P` | 命令面板 |
| `Ctrl+Shift+M` | 切换设备模式 |
| `F1` | DevTools 设置 |

## C. web-vitals 库使用指南

```bash
# 安装
npm install web-vitals
# 或
pnpm add web-vitals
```

```javascript
// 基础用法
import { onLCP, onCLS, onINP } from 'web-vitals';

onLCP(console.log);
onCLS(console.log);
onINP(console.log);

// 获取所有指标（适用于 SPA 路由切换时上报）
import { onLCP, onCLS, onINP, onFCP, onTTFB } from 'web-vitals';

function reportMetric(metric) {
  // metric 结构：
  // {
  //   name: 'LCP',
  //   value: 1234.56,      // 毫秒（CLS 除外）
  //   rating: 'good',      // 'good' | 'needs-improvement' | 'poor'
  //   delta: 1234.56,      // 与上次报告的差值
  //   id: 'v3-1234567890', // 唯一标识
  //   navigationType: 'navigate', // 导航类型
  //   entries: [...],      // PerformanceEntry 原始数据
  // }
}

onLCP(reportMetric);
onCLS(reportMetric);
onINP(reportMetric);
onFCP(reportMetric);
onTTFB(reportMetric);
```

## D. 推荐性能分析工具

| 工具 | 类型 | 用途 | 链接 |
|------|------|------|------|
| Chrome DevTools | 本地 | 综合性能分析 | 内置 |
| Lighthouse | 本地/CI | 性能审计与评分 | 内置 / [web.dev/measure](https://web.dev/measure/) |
| WebPageTest | 在线 | 真实设备多地点测试 | [webpagetest.org](https://www.webpagetest.org/) |
| PageSpeed Insights | 在线 | Core Web Vitals 数据 | [pagespeed.web.dev](https://pagespeed.web.dev/) |
| Search Console | 在线 | 线上 CWV 数据 | [search.google.com/search-console](https://search.google.com/search-console) |
| CrUX Dashboard | 在线 | Chrome 用户体验报告 | [chromium.org](https://chromium.org/) |
| SpeedCurve | 付费 | 持续性能监控 | [speedcurve.com](https://www.speedcurve.com/) |
| Calibre | 付费 | 团队性能监控 | [calibreapp.com](https://calibreapp.com/) |

## E. 性能优化检查清单

### 加载性能
- [ ] 关键 CSS 内联，非关键 CSS 异步加载
- [ ] 非关键 JS 使用 `defer` / `async`
- [ ] LCP 图片使用 `preload` + `fetchpriority="high"`
- [ ] 图片使用 WebP/AVIF 格式 + 响应式 `srcset`
- [ ] 启用文本压缩（Brotli/Gzip）
- [ ] 使用 CDN 分发静态资源
- [ ] 配置合适的缓存策略（Cache-Control）
- [ ] 减少关键路径资源数量

### 渲染性能
- [ ] 所有图片/视频设置明确尺寸或 `aspect-ratio`
- [ ] 字体使用 `font-display: swap` + `size-adjust`
- [ ] 广告/动态内容预留空间
- [ ] Cookie/通知横幅使用固定定位
- [ ] 避免强制同步布局（读写分离）
- [ ] 动画使用 `transform` / `opacity` / `filter`

### 交互性能
- [ ] 长任务拆分为多个短任务（<50ms）
- [ ] 耗时计算移入 Web Worker
- [ ] 搜索/筛选使用防抖/节流
- [ ] 长列表使用虚拟滚动
- [ ] 使用事件委托减少监听器
- [ ] 使用 `scheduler.yield()` 让出主线程

### 监控与维护
- [ ] 部署 RUM 监控（web-vitals）
- [ ] 设置性能预算
- [ ] 配置 CI 性能回归检测
- [ ] 定期审查 Core Web Vitals 数据
- [ ] 建立性能问题告警机制

---

> **文档版本**：v1.0
> **最后更新**：2025年
> **适用范围**：Chrome DevTools 120+、web-vitals 4.x、Core Web Vitals 2024 标准
