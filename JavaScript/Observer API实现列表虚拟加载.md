# Observer API 实现列表虚拟加载（Vue 3 版）

---

## 目录

1. [虚拟加载原理概述](#1-虚拟加载原理概述)
2. [核心机制详解](#2-核心机制详解)
3. [完整代码实现（Vue 3 组合式 API）](#3-完整代码实现vue-3-组合式-api)
4. [测试用例](#4-测试用例)
5. [性能优化与注意事项](#5-性能优化与注意事项)

---

## 1. 虚拟加载原理概述

### 1.1 什么是虚拟列表

虚拟列表（Virtual List / Virtual Scroll）是一种只渲染可视区域内的 DOM 节点，而非渲染全部数据项的技术。当列表数据量极大（如数万条）时，直接渲染全部节点会导致 DOM 节点过多，引发页面卡顿甚至崩溃。

```
┌─────────────────────────────────┐
│        滚动容器 (Container)      │
│  ┌───────────────────────────┐  │
│  │    不可见区域（上方）       │  │  ← 不渲染，用 paddingTop 占位
│  │         ...               │  │
│  ├───────────────────────────┤  │
│  │  ┌─────────────────────┐  │  │
│  │  │   Item 12  (渲染)    │  │  │
│  │  │   Item 13  (渲染)    │  │  │  ← 可视区域 (Viewport)
│  │  │   Item 14  (渲染)    │  │  │     只渲染可见的 DOM 节点
│  │  │   Item 15  (渲染)    │  │  │
│  │  │   Item 16  (渲染)    │  │  │
│  │  └─────────────────────┘  │  │
│  ├───────────────────────────┤  │
│  │    不可见区域（下方）       │  │  ← 不渲染，用 paddingBottom 占位
│  │         ...               │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

### 1.2 核心设计思路

| 阶段 | 操作 | 说明 |
|------|------|------|
| **初始化** | 计算容器高度、每项高度、可见项数 | 确定视口能容纳多少项 |
| **滚动时** | 计算 `startIndex` 和 `endIndex` | 确定当前需要渲染哪些项 |
| **渲染** | 只创建可见范围内的 DOM 节点 | 使用 `paddingTop` / `paddingBottom` 撑开滚动条 |
| **回收** | 移除不可见的 DOM 节点 | 配合 `top` 定位或 `transform` 实现偏移 |
| **数据加载** | 按需分片拉取数据 | 使用 IntersectionObserver 触发加载更多 |

### 1.3 两种实现方式对比

| 方式 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| **scroll 事件 + 计算** | 监听 `scroll`，计算 `startIndex`，动态更新 DOM | 兼容性好，控制精确 | 高频事件需防抖/节流 |
| **IntersectionObserver** | 哨兵元素进入/离开视口时触发回调 | 异步触发，性能优，不阻塞主线程 | 适用于"加载更多"场景 |

**本文采用混合方案**：`scroll` 事件 + 防抖实现虚拟滚动位置计算，`IntersectionObserver` 实现数据分片加载。

---

## 2. 核心机制详解

### 2.1 视口与尺寸计算

```
关键变量：
  containerHeight  — 滚动容器的高度（CSS 设置）
  itemHeight       — 每个列表项的固定高度（px）
  totalItems       — 数据总条数
  bufferSize       — 缓冲区：可视区域上下各多渲染的项数

计算公式：
  visibleCount = Math.ceil(containerHeight / itemHeight) + bufferSize * 2
  totalHeight  = totalItems * itemHeight
  scrollTop    = 容器的当前滚动距离

  startIndex   = Math.max(0, Math.floor(scrollTop / itemHeight) - bufferSize)
  endIndex     = Math.min(totalItems, startIndex + visibleCount)
  offsetY      = startIndex * itemHeight
```

```
scrollTop = 1200px, itemHeight = 50px, bufferSize = 3

  startIndex = Math.floor(1200 / 50) - 3 = 24 - 3 = 21
  offsetY = 21 * 50 = 1050px  ← paddingTop 撑开上方空间

  ┌──────────────────────────┐  ← scrollTop = 0
  │          ...             │
  │                          │  ← paddingTop = 1050px（不渲染占位）
  │                          │
  ├──────────────────────────┤  ← 实际渲染起始位置
  │  Item 21  (buffer)       │  ← 缓冲区（不可见但已渲染）
  │  Item 22  (buffer)       │
  │  Item 23  (buffer)       │
  │  Item 24  (visible)      │  ← 可视区域顶部
  │  Item 25  (visible)      │
  │  Item 26  (visible)      │
  │  ...                     │
  │  Item 33  (buffer)       │  ← 缓冲区
  │  Item 34  (buffer)       │
  │  Item 35  (buffer)       │
  ├──────────────────────────┤  ← 实际渲染结束位置
  │                          │  ← paddingBottom 撑开下方空间
  │          ...             │
  └──────────────────────────┘
```

### 2.2 可见范围计算逻辑

```ts
/**
 * 根据当前滚动位置计算需要渲染的项索引范围
 *
 * @param {number} scrollTop    - 当前滚动距离
 * @param {number} itemHeight   - 每项高度
 * @param {number} visibleCount - 可视区域可容纳的项数
 * @param {number} bufferSize   - 缓冲区大小
 * @param {number} totalItems   - 数据总条数
 * @returns {{ startIndex: number, endIndex: number, offsetY: number }}
 */
function computeVisibleRange(
  scrollTop: number,
  itemHeight: number,
  visibleCount: number,
  bufferSize: number,
  totalItems: number,
) {
  // 当前滚动位置对应的起始项索引（不含缓冲区）
  const rawStart = Math.floor(scrollTop / itemHeight);

  // 向上扩展缓冲区，确保不小于 0
  const startIndex = Math.max(0, rawStart - bufferSize);

  // 向下扩展缓冲区，确保不超过总数
  const endIndex = Math.min(totalItems, startIndex + visibleCount + bufferSize * 2);

  // 渲染区域上方的偏移量（用于 paddingTop 占位）
  const offsetY = startIndex * itemHeight;

  return { startIndex, endIndex, offsetY };
}
```

### 2.3 数据分片加载（IntersectionObserver）

使用 `IntersectionObserver` 监听哨兵元素（Sentinel），当哨兵进入视口时触发加载下一批数据。

```
┌──────────────────────────┐
│  Item 1                  │
│  Item 2                  │
│  ...                     │
│  Item 49                 │  ← 已加载数据
│  Item 50                 │
├──────────────────────────┤
│  ┌────────────────────┐  │
│  │  哨兵元素 (Sentinel) │  │  ← IntersectionObserver 监听
│  │  "加载中..."        │  │     进入视口 → 触发加载更多
│  └────────────────────┘  │
└──────────────────────────┘
```

### 2.4 DOM 动态创建与回收

```
滚动前：                        滚动后：
┌────────────────┐             ┌────────────────┐
│  Item 0  (渲染) │             │                 │  ← 回收：Item 0~3 移除
│  Item 1  (渲染) │             │  Item 4  (渲染) │
│  Item 2  (渲染) │   向下滚动   │  Item 5  (渲染) │
│  Item 3  (渲染) │  ────────►  │  Item 6  (渲染) │
│  Item 4  (渲染) │             │  Item 7  (渲染) │  ← 创建：Item 7 新建
│  Item 5  (渲染) │             │  Item 8  (渲染) │
│  Item 6  (渲染) │             │  Item 9  (渲染) │
└────────────────┘             └────────────────┘
```

回收策略：每次滚动时，对比新旧索引范围，利用 Vue 虚拟 DOM 自动 diff，避免手动 DOM 操作。

---

## 3. 完整代码实现（Vue 3 组合式 API）

### 3.1 VirtualList 组件 SFC

```vue
<!--
  VirtualList.vue —— 基于 Observer API 的 Vue 3 虚拟列表组件

  核心特性：
    - 仅渲染可视区域 + 缓冲区的 DOM 节点
    - 使用 IntersectionObserver 实现数据分片加载
    - 滚动事件防抖处理（rAF + requestAnimationFrame）
    - 支持作用域插槽自定义渲染、支持动态数据追加、暴露公共方法

  使用：
    <VirtualList
      :item-height="60"
      :buffer-size="5"
      :page-size="50"
      :fetch-data="mockFetchData"
      v-slot="{ item, index }"
    >
      <div class="list-item">
        <span>{{ index }}</span>
        <span>{{ item.name }}</span>
      </div>
    </VirtualList>
-->
<script setup lang="ts">
import {
  ref,
  shallowRef,
  reactive,
  computed,
  onMounted,
  onBeforeUnmount,
  nextTick,
  defineExpose,
  useTemplateRef,
} from 'vue';

// ==================== 类型定义 ====================

export interface FetchResult<T> {
  data: T[];
  total: number;
}

export interface VirtualListProps<T = any> {
  /** 单项高度（px），需为固定值 */
  itemHeight: number;
  /** 缓冲区大小（可视区上下各多渲染的项数），默认 5 */
  bufferSize?: number;
  /** 每次分片加载的数据条数，默认 50 */
  pageSize?: number;
  /** 防抖时间（ms），默认 16，约 60fps */
  debounceTime?: number;
  /**
   * 数据获取函数
   * 支持两种返回：{ data: [...], total: N } 或 纯数组
   */
  fetchData: (offset: number, limit: number) => Promise<T[] | FetchResult<T>>;
}

const props = withDefaults(defineProps<VirtualListProps>(), {
  bufferSize: 5,
  pageSize: 50,
  debounceTime: 16,
});

const slots = defineSlots<{
  default(props: { item: any; index: number }): any;
}>();

// ==================== 核心引用（DOM） ====================

const containerRef = useTemplateRef<HTMLDivElement>('containerRef');
const innerWrapperRef = useTemplateRef<HTMLDivElement>('innerWrapperRef');
const viewportRef = useTemplateRef<HTMLDivElement>('viewportRef');
const sentinelRef = useTemplateRef<HTMLDivElement>('sentinelRef');

// ==================== 响应式状态 ====================

// 数据
const dataList = shallowRef<any[]>([]);
const totalItems = ref(0);
const isLoading = ref(false);
const hasMore = ref(true);
const sentinelStatus = ref<'loading' | 'end' | 'error' | 'hidden'>('hidden');
const errorMsg = ref<string>('');

// 可视范围
const currentStartIndex = ref(-1);
const currentEndIndex = ref(-1);
const offsetY = ref(0);

// 视口容量（首次挂载时计算）
const visibleCount = ref(0);

// IntersectionObserver 实例
let observer: IntersectionObserver | null = null;

// 滚动防抖
let rafId: number | null = null;
let lastScrollTop = 0;

// ==================== 计算属性 ====================

/** 当前可视范围内的切片数组 + 带 index */
const visibleData = computed(() => {
  if (dataList.value.length === 0) return [];
  const start = currentStartIndex.value === -1 ? 0 : currentStartIndex.value;
  const end = currentEndIndex.value === -1
    ? Math.min(visibleCount.value, dataList.value.length)
    : currentEndIndex.value;
  return dataList.value.slice(start, end).map((item, idx) => ({
    item,
    index: start + idx,
  }));
});

/** 撑高层高度 = 总条数 × 单项高度 */
const totalHeight = computed(
  () => `${totalItems.value * props.itemHeight}px`,
);

/** viewport 的 transform 偏移 */
const viewportTransform = computed(
  () => `translateY(${offsetY.value}px)`,
);

// ==================== 工具：计算可见范围 ====================

function computeVisibleRange(scrollTop: number) {
  const rawStartIndex = Math.floor(scrollTop / props.itemHeight);
  const startIndex = Math.max(0, rawStartIndex - props.bufferSize);
  const endIndex = Math.min(
    dataList.value.length,
    rawStartIndex + visibleCount.value + props.bufferSize,
  );
  const offset = startIndex * props.itemHeight;
  return { startIndex, endIndex, offsetY: offset };
}

// ==================== 滚动处理（rAF 防抖） ====================

function handleScroll() {
  if (!containerRef.value) return;

  const scrollTop = containerRef.value.scrollTop;
  if (scrollTop === lastScrollTop) return;
  lastScrollTop = scrollTop;

  // 合并同一帧内的多次 scroll 事件
  if (rafId != null) return;

  rafId = requestAnimationFrame(() => {
    rafId = null;
    if (dataList.value.length === 0) return;

    const range = computeVisibleRange(lastScrollTop);

    // 范围没有变化则跳过，避免触发响应式更新
    if (
      range.startIndex === currentStartIndex.value
      && range.endIndex === currentEndIndex.value
    ) {
      return;
    }

    currentStartIndex.value = range.startIndex;
    currentEndIndex.value = range.endIndex;
    offsetY.value = range.offsetY;
  });
}

// ==================== 数据加载 ====================

async function loadMore() {
  if (isLoading.value || !hasMore.value) return;

  isLoading.value = true;
  sentinelStatus.value = 'loading';
  errorMsg.value = '';

  try {
    const result = await props.fetchData(dataList.value.length, props.pageSize);

    if (Array.isArray(result)) {
      dataList.value = [...dataList.value, ...result];
      totalItems.value = dataList.value.length;
    } else {
      dataList.value = [...dataList.value, ...result.data];
      totalItems.value = result.total;
    }

    hasMore.value = dataList.value.length < totalItems.value;

    // 数据不足一屏，继续加载
    if (hasMore.value && dataList.value.length < visibleCount.value * 2) {
      isLoading.value = false;
      await loadMore();
      return;
    }

    // 首次渲染：立即计算可见范围
    if (currentStartIndex.value === -1) {
      applyInitialRender();
    }

    // 全部加载完成
    if (!hasMore.value) {
      sentinelStatus.value = 'end';
    } else {
      // 数据已加载，哨兵回到 loading 态（后续 IntersectionObserver 驱动）
      sentinelStatus.value = 'loading';
    }
  } catch (e: any) {
    console.error('[VirtualList] 数据加载失败:', e);
    errorMsg.value = e?.message ?? '未知错误';
    sentinelStatus.value = 'error';
  } finally {
    isLoading.value = false;
  }
}

function applyInitialRender() {
  const scrollTop = containerRef.value?.scrollTop ?? 0;
  const range = computeVisibleRange(scrollTop);
  currentStartIndex.value = range.startIndex;
  currentEndIndex.value = range.endIndex;
  offsetY.value = range.offsetY;
}

// ==================== IntersectionObserver 回调 ====================

function handleIntersection(entries: IntersectionObserverEntry[]) {
  for (const entry of entries) {
    if (entry.isIntersecting && !isLoading.value && hasMore.value) {
      loadMore();
    }
  }
}

// ==================== 生命周期 ====================

onMounted(async () => {
  if (!containerRef.value || !sentinelRef.value) return;

  // 计算可视容量
  const containerH = containerRef.value.clientHeight;
  visibleCount.value = Math.ceil(containerH / props.itemHeight) + props.bufferSize * 2;

  // 绑定滚动事件（passive：告知浏览器不会 preventDefault，提升滚动性能）
  containerRef.value.addEventListener('scroll', handleScroll, { passive: true });

  // 创建 IntersectionObserver
  observer = new IntersectionObserver(handleIntersection, {
    root: containerRef.value,
    rootMargin: '100px',
    threshold: 0,
  });
  observer.observe(sentinelRef.value);

  // 首屏加载
  await loadMore();
});

onBeforeUnmount(() => {
  // 清理 rAF
  if (rafId != null) {
    cancelAnimationFrame(rafId);
    rafId = null;
  }

  // 取消 IntersectionObserver
  if (observer) {
    observer.disconnect();
    observer = null;
  }

  // 移除 scroll 监听
  if (containerRef.value) {
    containerRef.value.removeEventListener('scroll', handleScroll);
  }
});

// ==================== 公共方法（父组件可通过 ref 调用） ====================

/** 重置列表：清空数据重新加载 */
async function reset() {
  dataList.value = [];
  totalItems.value = 0;
  hasMore.value = true;
  currentStartIndex.value = -1;
  currentEndIndex.value = -1;
  offsetY.value = 0;

  if (containerRef.value) {
    containerRef.value.scrollTo({ top: 0, behavior: 'auto' });
  }
  sentinelStatus.value = 'loading';
  await nextTick();
  await loadMore();
}

/** 滚动到指定索引 */
function scrollToIndex(index: number, smooth = true) {
  if (!containerRef.value) return;
  containerRef.value.scrollTo({
    top: index * props.itemHeight,
    behavior: smooth ? 'smooth' : 'auto',
  });
}

/** 手动触发重试（error 态下） */
function retry() {
  loadMore();
}

defineExpose({
  reset,
  scrollToIndex,
  retry,
  // 只读状态，方便调试
  data: dataList,
  totalItems,
  isLoading,
  hasMore,
  currentStartIndex,
  currentEndIndex,
});
</script>

<template>
  <!-- 外层滚动容器：用户可通过 class/style 控制高度等 -->
  <div
    ref="containerRef"
    class="vl-container"
    :style="{ position: 'relative', overflow: 'auto' }"
  >
    <!-- 撑高层：用于撑开滚动条 -->
    <div
      ref="innerWrapperRef"
      class="vl-inner"
      :style="{ position: 'relative', height: totalHeight }"
    >
      <!-- 可视渲染层：通过 GPU 加速 transform 定位 -->
      <div
        ref="viewportRef"
        class="vl-viewport"
        :style="{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          willChange: 'transform',
          transform: viewportTransform,
        }"
      >
        <!--
          注意：每个 item 使用 absolute + top(i*itemHeight) 定位，
          因为 viewport 自身已被 translateY(offsetY)，所以实际 i*itemHeight
          就已经把它放置在文档流的正确位置。
        -->
        <div
          v-for="{ item, index } in visibleData"
          :key="index"
          class="vl-item"
          :style="{
            position: 'absolute',
            top: `${index * props.itemHeight}px`,
            left: 0,
            right: 0,
            height: `${props.itemHeight}px`,
            overflow: 'hidden',
            boxSizing: 'border-box',
          }"
        >
          <slot :item="item" :index="index">
            <!-- 默认渲染：若未提供插槽 -->
            <div style="padding: 8px 12px; border-bottom: 1px solid #eee; background: index % 2 === 0 ? '#f9f9f9' : '#fff'">
              <span style="color:#999;margin-right:8px;">#{{ index }}</span>
              <span>{{ JSON.stringify(item) }}</span>
            </div>
          </slot>
        </div>
      </div>
    </div>

    <!-- 哨兵元素：IntersectionObserver 观察对象 -->
    <div ref="sentinelRef" class="vl-sentinel">
      <template v-if="sentinelStatus === 'loading'">
        <div class="vl-sentinel-content">
          <svg viewBox="0 0 24 24" class="vl-spinner" width="16" height="16">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" />
          </svg>
          <span>加载中...</span>
        </div>
      </template>
      <template v-else-if="sentinelStatus === 'end'">
        <div class="vl-sentinel-content vl-sentinel-end">— 已加载全部数据 —</div>
      </template>
      <template v-else-if="sentinelStatus === 'error'">
        <div class="vl-sentinel-content vl-sentinel-error">
          加载失败{{ errorMsg ? `：${errorMsg}` : '' }}
          <button class="vl-retry-btn" @click="retry">点击重试</button>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.vl-container {
  width: 100%;
  /* 高度需要父组件通过 style/class 覆盖 */
}

.vl-container::-webkit-scrollbar {
  width: 6px;
}
.vl-container::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.vl-sentinel {
  width: 100%;
  min-height: 1px;
  flex-shrink: 0;
}

.vl-sentinel-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  color: #999;
  font-size: 13px;
}

.vl-sentinel-end {
  color: #ccc;
}

.vl-sentinel-error {
  color: #f44336;
}

.vl-retry-btn {
  cursor: pointer;
  color: #1890ff;
  border: none;
  background: none;
  text-decoration: underline;
  padding: 0 4px;
}

.vl-retry-btn:active {
  opacity: 0.7;
}

/* loading 图标旋转动画 */
@keyframes vl-spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

.vl-spinner {
  color: #1890ff;
  animation: vl-spin 1s linear infinite;
  stroke-dasharray: 40 60;
  stroke-dashoffset: 20;
}
</style>
```

### 3.2 使用示例（Vue 3 App.vue）

```vue
<!--
  App.vue —— VirtualList 使用示例
  场景：渲染 100,000 条用户数据，只渲染可视区域
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import VirtualList from './VirtualList.vue';

// ==================== 模拟服务端数据接口 ====================

const TOTAL_ITEMS = 100_000;
const PAGE_SIZE = 50;

interface UserItem {
  id: number;
  name: string;
  email: string;
  desc: string;
  avatar: string;
}

/**
 * 模拟异步分页接口
 * （实际项目中这里换成 axios 或 fetch 请求即可）
 */
function mockFetchData(offset: number, limit: number) {
  return new Promise<{ data: UserItem[]; total: number }>((resolve) => {
    const delay = 250 + Math.random() * 200;

    setTimeout(() => {
      const end = Math.min(offset + limit, TOTAL_ITEMS);
      const items: UserItem[] = [];
      for (let i = offset; i < end; i++) {
        items.push({
          id: i,
          name: `用户 ${String(i + 1).padStart(6, '0')}`,
          email: `user${i + 1}@example.com`,
          desc: `这是第 ${i + 1} 条数据的描述信息，用于展示虚拟列表的长文本截断效果。`,
          // A-Z 循环
          avatar: String.fromCodePoint(65 + (i % 26)),
        });
      }
      resolve({ data: items, total: TOTAL_ITEMS });
    }, delay);
  });
}

// ==================== 虚拟列表 ref（调用公共方法） ====================

const vListRef = ref<InstanceType<typeof VirtualList> | null>(null);

// 统计信息
const stats = computed(() => {
  const list = vListRef.value;
  if (!list) return { loaded: 0, total: TOTAL_ITEMS, rendered: 0 };
  return {
    loaded: list.data.length,
    total: list.totalItems,
    rendered: (list.currentEndIndex - list.currentStartIndex) > 0
      ? list.currentEndIndex - list.currentStartIndex
      : 0,
  };
});

// ==================== 公共方法演示 ====================

function handleReset() {
  vListRef.value?.reset();
}

function handleScrollTo() {
  const idx = window.prompt('请输入要跳转到的索引（0 - 99999）');
  if (idx == null) return;
  const n = Number(idx);
  if (!Number.isNaN(n) && n >= 0) vListRef.value?.scrollToIndex(n);
}

// 定时刷新统计（仅用于演示）
const tick = ref(0);
onMounted(() => {
  setInterval(() => { tick.value++; }, 500);
});
const _ = tick; // 保证响应式
</script>

<template>
  <div class="app">
    <!-- 顶部操作栏 -->
    <header class="app-header">
      <h2 class="app-title">Vue 3 虚拟列表（Observer API）</h2>
      <div class="app-actions">
        <button class="btn btn-primary" @click="handleReset">重置</button>
        <button class="btn" @click="handleScrollTo">跳转到索引</button>
      </div>
      <div class="app-stats">
        已加载：{{ stats.loaded.toLocaleString() }} / {{ stats.total.toLocaleString() }}
        &nbsp;·&nbsp;
        正在渲染：{{ stats.rendered }} 个节点
      </div>
    </header>

    <!-- 虚拟列表：高度 500px + 单项 60px + 自定义插槽 -->
    <VirtualList
      ref="vListRef"
      :item-height="60"
      :buffer-size="5"
      :page-size="PAGE_SIZE"
      :fetch-data="mockFetchData"
      style="height: 500px; border: 1px solid #eee; border-radius: 8px;"
      v-slot="{ item, index }"
    >
      <div class="user-item" :class="{ odd: index % 2 === 0 }">
        <!-- 头像 -->
        <div class="item-avatar">{{ item.avatar }}</div>
        <!-- 信息 -->
        <div class="item-info">
          <div class="item-name">
            {{ item.name }}
            <span class="item-email">{{ item.email }}</span>
          </div>
          <div class="item-desc" :title="item.desc">{{ item.desc }}</div>
        </div>
        <!-- 索引 -->
        <span class="item-index">#{{ index }}</span>
      </div>
    </VirtualList>
  </div>
</template>

<style scoped>
.app {
  max-width: 720px;
  margin: 24px auto;
  padding: 0 16px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
}

.app-header {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px 20px;
  margin-bottom: 12px;
  display: grid;
  grid-template-columns: 1fr auto;
  grid-template-rows: auto auto;
  row-gap: 8px;
}
.app-title {
  grid-column: 1;
  margin: 0;
  font-size: 18px;
  color: #333;
}
.app-actions {
  grid-column: 2;
  grid-row: 1 / span 2;
  align-self: center;
  display: flex;
  gap: 8px;
}
.app-stats {
  grid-column: 1;
  font-size: 12px;
  color: #888;
}

.btn {
  cursor: pointer;
  padding: 6px 14px;
  border-radius: 4px;
  border: 1px solid #d9d9d9;
  background: #fff;
  font-size: 13px;
  color: #333;
  transition: all 0.15s;
}
.btn:hover {
  border-color: #1890ff;
  color: #1890ff;
}
.btn-primary {
  background: #1890ff;
  color: #fff;
  border-color: #1890ff;
}
.btn-primary:hover {
  background: #40a9ff;
  color: #fff;
}

/* 列表项样式 */
.user-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
  color: #333;
  height: 100%;
  transition: background-color 0.15s;
  background: #fff;
}
.user-item.odd {
  background: #fafafa;
}
.user-item:hover {
  background: #e6f7ff;
}

.item-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 12px;
  flex-shrink: 0;
}

.item-info {
  flex: 1;
  min-width: 0;
}
.item-name {
  font-weight: 500;
  margin-bottom: 2px;
}
.item-email {
  color: #1890ff;
  font-size: 12px;
  font-weight: normal;
  margin-left: 8px;
}
.item-desc {
  font-size: 12px;
  color: #999;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.item-index {
  font-size: 12px;
  color: #bbb;
  margin-left: 8px;
  flex-shrink: 0;
}
</style>
```

### 3.3 Vue 3 可复用的 composable（高阶用法）

如果想在多个页面共享滚动 + Observer 的逻辑，可以把核心算法抽成 composable：

```ts
// useVirtualList.ts
import { ref, shallowRef, computed, onMounted, onBeforeUnmount } from 'vue';

export function useVirtualList<T = any>(options: {
  itemHeight: number;
  bufferSize?: number;
  pageSize?: number;
  fetchData: (offset: number, limit: number) => Promise<T[] | { data: T[]; total: number }>;
}) {
  const { itemHeight, bufferSize = 5, pageSize = 50, fetchData } = options;

  const data = shallowRef<T[]>([]);
  const total = ref(0);
  const isLoading = ref(false);
  const hasMore = ref(true);

  const startIndex = ref(-1);
  const endIndex = ref(-1);
  const offsetY = ref(0);
  const visibleCount = ref(0);

  let containerEl: HTMLElement | null = null;
  let observer: IntersectionObserver | null = null;
  let rafId: number | null = null;

  // 可见切片
  const visibleData = computed(() => {
    const s = startIndex.value < 0 ? 0 : startIndex.value;
    const e = endIndex.value < 0 ? visibleCount.value : endIndex.value;
    return data.value.slice(s, e).map((item, idx) => ({ item, index: s + idx }));
  });

  function computeRange(scrollTop: number) {
    const raw = Math.floor(scrollTop / itemHeight);
    const s = Math.max(0, raw - bufferSize);
    const e = Math.min(data.value.length, raw + visibleCount.value + bufferSize);
    return { startIndex: s, endIndex: e, offsetY: s * itemHeight };
  }

  function onScroll(e: Event) {
    const el = e.currentTarget as HTMLElement;
    const top = el.scrollTop;
    if (rafId != null) return;
    rafId = requestAnimationFrame(() => {
      rafId = null;
      const r = computeRange(top);
      if (r.startIndex === startIndex.value && r.endIndex === endIndex.value) return;
      startIndex.value = r.startIndex;
      endIndex.value = r.endIndex;
      offsetY.value = r.offsetY;
    });
  }

  async function loadMore() {
    if (isLoading.value || !hasMore.value) return;
    isLoading.value = true;
    try {
      const res = await fetchData(data.value.length, pageSize);
      if (Array.isArray(res)) {
        data.value = [...data.value, ...res];
        total.value = data.value.length;
      } else {
        data.value = [...data.value, ...res.data];
        total.value = res.total;
      }
      hasMore.value = data.value.length < total.value;
      if (startIndex.value < 0) {
        const r = computeRange(0);
        startIndex.value = r.startIndex;
        endIndex.value = r.endIndex;
        offsetY.value = r.offsetY;
      }
    } finally {
      isLoading.value = false;
    }
  }

  function setup(el: HTMLElement, sentinelEl: HTMLElement) {
    containerEl = el;
    visibleCount.value = Math.ceil(el.clientHeight / itemHeight) + bufferSize * 2;
    el.addEventListener('scroll', onScroll, { passive: true });
    observer = new IntersectionObserver((entries) => {
      entries.forEach((en) => en.isIntersecting && loadMore());
    }, { root: el, rootMargin: '100px', threshold: 0 });
    observer.observe(sentinelEl);
    loadMore();
  }

  function cleanup() {
    if (rafId != null) cancelAnimationFrame(rafId);
    if (observer) observer.disconnect();
    if (containerEl) containerEl.removeEventListener('scroll', onScroll);
  }

  function reset() {
    data.value = [];
    total.value = 0;
    hasMore.value = true;
    startIndex.value = -1;
    endIndex.value = -1;
    loadMore();
  }

  onMounted(() => {}); // NOOP，setup 由调用方在合适时机触发
  onBeforeUnmount(cleanup);

  return {
    data, total, isLoading, hasMore,
    startIndex, endIndex, offsetY, visibleCount,
    visibleData,
    totalHeight: computed(() => `${total.value * itemHeight}px`),
    viewportTransform: computed(() => `translateY(${offsetY.value}px)`),
    setup, cleanup, reset, loadMore,
  };
}
```

---

## 4. 测试用例

### 4.1 单元测试（Vitest + @vue/test-utils）

```ts
// __tests__/VirtualList.spec.ts
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import { nextTick, ref } from 'vue';
import VirtualList from '../VirtualList.vue';

// ---- 辅助：模拟 IntersectionObserver ----
const mockObserverEntries: IntersectionObserverEntry[] = [];
let observerCallback: IntersectionObserverCallback | null = null;

function mockIntersectionObserver() {
  const IntersectionObserverMock = vi.fn((cb: IntersectionObserverCallback) => {
    observerCallback = cb;
    return {
      observe: vi.fn(),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
      takeRecords: vi.fn(() => mockObserverEntries),
    };
  });
  window.IntersectionObserver = IntersectionObserverMock as any;
}

function triggerIntersect(isIntersecting: boolean = true) {
  if (!observerCallback) return;
  observerCallback([{
    isIntersecting,
    intersectionRatio: isIntersecting ? 1 : 0,
    target: document.createElement('div'),
    boundingClientRect: {} as DOMRectReadOnly,
    intersectionRect: {} as DOMRectReadOnly,
    rootBounds: null,
    time: 0,
  }], {
    // 简化版 observer 实例
  } as IntersectionObserver);
}

// ---- 模拟数据 ----
function mockFetch(offset: number, limit: number) {
  const TOTAL = 1000;
  const end = Math.min(offset + limit, TOTAL);
  return Promise.resolve({
    data: Array.from({ length: end - offset }, (_, i) => ({
      id: offset + i,
      name: `User ${offset + i + 1}`,
    })),
    total: TOTAL,
  });
}

describe('VirtualList (Vue 3)', () => {
  beforeEach(() => {
    mockIntersectionObserver();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  // ---------- 测试 1：首屏渲染 ----------
  it('[首屏] 挂载后应该加载首批数据，并渲染首批可视项', async () => {
    const ITEM_H = 50;
    const wrapper = mount(VirtualList, {
      props: {
        itemHeight: ITEM_H,
        bufferSize: 3,
        pageSize: 50,
        fetchData: mockFetch,
      },
      global: {
        stubs: { teleport: true },
      },
      attrs: {
        style: 'height: 400px;',
      },
    });

    // 容器的 clientHeight 需手动 mock（jsdom 默认 0）
    const container = wrapper.find<HTMLDivElement>({ ref: 'containerRef' });
    Object.defineProperty(container.element, 'clientHeight', { value: 400, configurable: true });

    // 触发 onMounted：手动触发首屏加载
    await flushPromises();

    // 触发 IntersectionObserver 进入视口（首屏加载会调用一次）
    triggerIntersect(true);
    await flushPromises();
    await nextTick();

    const list: any = wrapper.vm;
    // 首屏 data 应有 1 页（50 条）
    expect(list.data.length).toBeGreaterThan(0);

    // currentStartIndex/EndIndex 已经设置
    expect(list.currentStartIndex).toBe(0);
    expect(list.currentEndIndex).toBeGreaterThan(0);
  });

  // ---------- 测试 2：可见范围计算 ----------
  it('[计算] scrollTop=500、itemHeight=50、bufferSize=3 时，startIndex 应为 7', async () => {
    const wrapper = mount(VirtualList, {
      props: {
        itemHeight: 50,
        bufferSize: 3,
        pageSize: 50,
        fetchData: mockFetch,
      },
      attrs: { style: 'height: 400px;' },
    });

    const container = wrapper.find<HTMLDivElement>({ ref: 'containerRef' });
    Object.defineProperty(container.element, 'clientHeight', { value: 400, configurable: true });

    triggerIntersect(true);
    await flushPromises();
    await nextTick();

    const list: any = wrapper.vm;

    // 模拟 scrollTop = 500
    Object.defineProperty(container.element, 'scrollTop', { value: 500, writable: true, configurable: true });
    container.trigger('scroll');

    // 等待 requestAnimationFrame 执行
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    await nextTick();

    // startIndex = Math.floor(500/50) - 3 = 10 - 3 = 7
    expect(list.currentStartIndex).toBe(7);
    // offsetY = 7 * 50 = 350
    expect(list.offsetY).toBe(350);
  });

  // ---------- 测试 3：不会渲染超过可视 + 缓冲范围的 DOM ----------
  it('[渲染] DOM 节点数应约等于可见项数，而非全部数据', async () => {
    const wrapper = mount(VirtualList, {
      props: {
        itemHeight: 50,
        bufferSize: 3,
        pageSize: 200,
        fetchData: async (off, limit) => mockFetch(off, limit),
      },
      attrs: { style: 'height: 400px;' },
    });

    const container = wrapper.find<HTMLDivElement>({ ref: 'containerRef' });
    Object.defineProperty(container.element, 'clientHeight', { value: 400, configurable: true });

    triggerIntersect(true);
    await flushPromises();
    await nextTick();

    // 找到所有 item（类名 vl-item 的绝对定位项）
    const items = wrapper.findAll('.vl-item');
    const list: any = wrapper.vm;
    // 可见 DOM 应远小于总数据（200）
    expect(items.length).toBeLessThan(200);
    // 并等于 currentEndIndex - currentStartIndex
    const rendered = list.currentEndIndex - list.currentStartIndex;
    expect(items.length).toBe(rendered);
  });

  // ---------- 测试 4：reset 应清空并重新加载 ----------
  it('[重置] 调用 reset() 后，数据应该被清空并重新加载', async () => {
    const fetchSpy = vi.fn(mockFetch);
    const wrapper = mount(VirtualList, {
      props: {
        itemHeight: 50,
        bufferSize: 3,
        pageSize: 50,
        fetchData: fetchSpy,
      },
      attrs: { style: 'height: 400px;' },
    });

    triggerIntersect(true);
    await flushPromises();
    await nextTick();

    const list: any = wrapper.vm;
    expect(fetchSpy).toHaveBeenCalledTimes(1);

    // 调用 reset
    list.reset();
    await flushPromises();
    await nextTick();

    expect(fetchSpy).toHaveBeenCalledWith(0, 50); // 重置后应从 offset 0 重新拉
    expect(fetchSpy).toHaveBeenCalled();
  });

  // ---------- 测试 5：无更多数据时哨兵状态为 end ----------
  it('[哨兵] 数据加载完成时，sentinelStatus 应为 end', async () => {
    // 返回只有 30 条的小数据集
    const smallFetch = (offset: number, limit: number) => Promise.resolve({
      data: Array.from({ length: Math.min(limit, 30 - offset) }, (_, i) => ({ id: offset + i })),
      total: 30,
    });

    const wrapper = mount(VirtualList, {
      props: {
        itemHeight: 50,
        bufferSize: 2,
        pageSize: 50,  // 一页就装完
        fetchData: smallFetch,
      },
      attrs: { style: 'height: 400px;' },
    });

    const container = wrapper.find<HTMLDivElement>({ ref: 'containerRef' });
    Object.defineProperty(container.element, 'clientHeight', { value: 400, configurable: true });

    triggerIntersect(true);
    await flushPromises();
    await nextTick();

    const list: any = wrapper.vm;
    expect(list.hasMore).toBe(false);
    expect(list.sentinelStatus).toBe('end');
  });

  // ---------- 测试 6：滚动不超出数据边界 ----------
  it('[边界] 计算的 endIndex 不超过 data 长度，startIndex 不小于 0', async () => {
    const wrapper = mount(VirtualList, {
      props: { itemHeight: 50, bufferSize: 3, pageSize: 10, fetchData: mockFetch },
      attrs: { style: 'height: 400px;' },
    });

    const container = wrapper.find<HTMLDivElement>({ ref: 'containerRef' });
    Object.defineProperty(container.element, 'clientHeight', { value: 400, configurable: true });

    triggerIntersect(true);
    await flushPromises();
    await nextTick();

    const list: any = wrapper.vm;

    // 滚动到极底部
    Object.defineProperty(container.element, 'scrollTop', { value: 1_000_000, writable: true, configurable: true });
    container.trigger('scroll');
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    await nextTick();

    expect(list.currentStartIndex).toBeGreaterThanOrEqual(0);
    expect(list.currentEndIndex).toBeLessThanOrEqual(list.data.length + 1);
  });
});
```

### 4.2 性能测试（浏览器控制台）

```vue
<!--
  PerformanceCompare.vue —— 虚拟列表 vs 普通列表性能对比
-->
<script setup lang="ts">
import { ref, onMounted } from 'vue';

const result = ref('');

async function run() {
  const DATA_SIZE = 10_000;
  const ITEM_H = 50;
  const CONTAINER_H = 400;

  const lines: string[] = [];
  lines.push('='.repeat(60));
  lines.push('性能对比：虚拟列表 vs 普通列表');
  lines.push('='.repeat(60));

  // ====== 普通列表 ======
  lines.push('\n[普通列表] 全量渲染 10,000 项...');
  const normalEl = document.createElement('div');
  normalEl.style.cssText = `height:${CONTAINER_H}px;overflow:auto;position:absolute;left:-9999px;top:0;`;
  document.body.appendChild(normalEl);

  const nStart = performance.now();
  const frag = document.createDocumentFragment();
  for (let i = 0; i < DATA_SIZE; i++) {
    const d = document.createElement('div');
    d.style.height = `${ITEM_H}px`;
    d.textContent = `Item ${i}`;
    frag.appendChild(d);
  }
  normalEl.appendChild(frag);
  const nEnd = performance.now();

  const nTime = nEnd - nStart;
  const nCount = normalEl.children.length;
  lines.push(`  渲染耗时: ${nTime.toFixed(1)}ms`);
  lines.push(`  DOM 节点数: ${nCount}`);

  // 滚动性能
  const nsStart = performance.now();
  for (const t of [10000, 20000, 30000]) {
    normalEl.scrollTop = t;
    await new Promise((r) => requestAnimationFrame(r));
  }
  const nsEnd = performance.now();
  lines.push(`  3 次滚动耗时: ${(nsEnd - nsStart).toFixed(1)}ms`);
  document.body.removeChild(normalEl);

  // ====== 虚拟列表（直接使用算法，不挂载组件） ======
  lines.push('\n[虚拟列表] 按需渲染 10,000 项...');

  const data: any[] = Array.from({ length: DATA_SIZE }, (_, i) => ({ id: i }));
  const bufferSize = 5;
  const visibleCount = Math.ceil(CONTAINER_H / ITEM_H) + bufferSize * 2; // 8 + 10 = 18

  function computeRange(top: number) {
    const raw = Math.floor(top / ITEM_H);
    return {
      startIndex: Math.max(0, raw - bufferSize),
      endIndex: Math.min(data.length, raw + visibleCount + bufferSize),
      offsetY: Math.max(0, raw - bufferSize) * ITEM_H,
    };
  }

  // 首次渲染
  const vStart = performance.now();
  const r0 = computeRange(0);
  const initialSlice = data.slice(r0.startIndex, r0.endIndex);
  const vDOMCount = initialSlice.length;
  // 模拟构建 DOM 的耗时（实际 Vue 会有 vDOM diff）
  const vEnd = performance.now();

  // 滚动性能
  const vsStart = performance.now();
  for (const t of [10000, 20000, 30000]) {
    computeRange(t);
    await new Promise((r) => requestAnimationFrame(r));
  }
  const vsEnd = performance.now();

  lines.push(`  渲染 DOM 节点数: ${vDOMCount}`);
  lines.push(`  3 次滚动计算耗时: ${(vsEnd - vsStart).toFixed(1)}ms`);

  lines.push('\n' + '='.repeat(60));
  lines.push('对比结果:');
  const pct = ((1 - vDOMCount / nCount) * 100).toFixed(1);
  lines.push(`  DOM 节点数:  普通 ${nCount}  vs  虚拟 ${vDOMCount}  (减少 ${pct}%)`);
  lines.push(`  渲染耗时:    普通 ${nTime.toFixed(1)}ms  vs  虚拟 ${(vEnd - vStart).toFixed(1)}ms`);
  lines.push('='.repeat(60));

  result.value = lines.join('\n');
}

onMounted(run);
</script>

<template>
  <pre style="background:#1e1e1e;color:#d4d4d4;padding:20px;border-radius:8px;overflow:auto;">
    {{ result }}
  </pre>
</template>
```

### 4.3 快速滚动压力测试

```ts
// stress.ts —— 可在浏览器控制台直接运行，或封装为组件
import { ref, onMounted } from 'vue';

export function useStressTest(buildList: () => any) {
  const report = ref('');

  async function run() {
    const buf: string[] = [];
    buf.push('='.repeat(60));
    buf.push('Vue 3 VirtualList 快速滚动压力测试');
    buf.push('='.repeat(60));

    const list = buildList(); // 外部创建并挂载组件后传入实例
    let errors = 0;

    // 模拟快速滚动的 scrollTop 序列
    const positions = [0, 500, 1500, 3000, 6000, 10000, 20000, 35000, 50000, 80000];

    const t0 = performance.now();
    for (const pos of positions) {
      list.scrollToIndex(Math.floor(pos / 60), false);
      await new Promise((r) => requestAnimationFrame(r));

      // 校验可视范围边界
      if (list.currentStartIndex.value < 0) {
        buf.push(`  ✗ scrollTop=${pos} startIndex 非法: ${list.currentStartIndex.value}`);
        errors++;
      }
      if (list.currentEndIndex.value > list.data.value.length) {
        buf.push(`  ✗ scrollTop=${pos} endIndex 越界: ${list.currentEndIndex.value}`);
        errors++;
      }
    }
    const t1 = performance.now();

    buf.push(`  滚动位置数: ${positions.length}`);
    buf.push(`  总耗时: ${(t1 - t0).toFixed(1)}ms`);
    buf.push(`  平均耗时: ${((t1 - t0) / positions.length).toFixed(1)}ms/次`);
    buf.push(`  错误数: ${errors}`);
    buf.push(errors === 0 ? '  结果: 通过' : `  结果: 失败 — ${errors} 个错误`);
    report.value = buf.join('\n');
  }

  onMounted(run);
  return { report, run };
}
```

---

## 5. 性能优化与注意事项

### 5.1 优化策略总结

| 优化点 | Vue 3 实现方式 | 预期效果 |
|--------|----------|----------|
| **DOM 节点数控制** | `visibleData` 只切片可视区域 + 缓冲区 | 10,000 条数据仅渲染 ~20 个节点 |
| **滚动事件防抖** | `requestAnimationFrame` 合并同帧 scroll | ~60fps 更新，避免多余计算 |
| **增量更新** | Vue 虚拟 DOM diff + `:key="index"` 稳定 | 只更新变化项，减少重建 |
| **定位性能** | `transform: translateY()` + `will-change: transform` | 只触发 Composite，跳过 Layout/Paint |
| **数据分片加载** | `IntersectionObserver` 哨兵元素 | 异步回调，不阻塞主线程 |
| **响应式性能** | `dataList` 用 `shallowRef`，不深度代理 | 大数据量下响应式开销为 O(1) |
| **passive 事件** | `addEventListener(..., { passive: true })` | 告知浏览器不调 `preventDefault`，滚动更流畅 |
| **作用域样式隔离** | `<style scoped>` 自动加作用域属性 | 避免全局样式污染，生产级安全 |

### 5.2 Vue 3 响应式优化提示

```
传统 ref：     ref([ 10万条对象 ]) → 全量递归 Proxy → 首次赋值 O(N) 开销大
shallowRef： shallowRef(...)    → 只代理最外层数组，内部对象不代理
                                 → + 解构时 .value 返回原数组，响应式只追踪数组引用变化
```

建议：
- 列表数据（只读或整体替换）优先用 `shallowRef`，内存/性能提升明显。
- 若需要单项细粒度响应式（如行内编辑），再切换为 `ref` 或使用 `markRaw` 局部控制。

### 5.3 GPU 加速原理

```
传统方式（top）：
  scroll → 改 top → 触发 Layout → 触发 Paint → 触发 Composite

Vue 3 方式（transform）：
  scroll → 修改 style.transform → 直接 Composite（跳过 Layout 和 Paint）
  再加 will-change: transform → 浏览器提前分配图层 & GPU 光栅化
```

### 5.4 注意事项

1. **固定高度约束**：本实现假设每项高度固定。若需不定高，需用 `ResizeObserver` 维护每项实际高度和累加偏移数组，并将 `computeVisibleRange` 改为二分查找定位。

2. **数据一致性**：`totalItems` 应与服务端一致。若滚动中服务端数据增删，需重新计算 `totalHeight` 并重新应用当前可见范围。

3. **缓冲区大小**：`bufferSize` 过小 → 快速滚动可能短暂白屏；过大 → DOM 节点增多。建议设置为可视区项数的 0.5~1 倍。

4. **IntersectionObserver 兼容性**：IE 不支持；如须兼容 IE 11，可降级为 `scroll` 事件判断「哨兵是否进入容器视口」或加载 polyfill。

5. **SSR（Nuxt 3）兼容**：虚拟列表依赖浏览器 API（滚动容器的 `clientHeight`、`IntersectionObserver`、`requestAnimationFrame`）。在 SSR 阶段应返回空壳；在客户端 hydrate 后（`onMounted`）再初始化和加载首屏数据。

6. **组件卸载清理**：`onBeforeUnmount` 必须 `cancelAnimationFrame` + `observer.disconnect()` + 移除 `scroll` 监听，否则路由离开后会内存泄漏。

### 5.5 扩展到不定高列表（Vue 3 组合式）

```vue
<!-- DynamicHeightVirtualList.vue —— 不定高虚拟列表骨架（可继承/重写） -->
<script setup lang="ts">
import { ref, shallowRef, onMounted, nextTick } from 'vue';

interface Props {
  estimatedItemHeight?: number;
  bufferSize?: number;
  fetchData: (offset: number, limit: number) => Promise<any[]>;
}
const props = withDefaults(defineProps<Props>(), {
  estimatedItemHeight: 60,
  bufferSize: 3,
});

// 每项真实高度缓存（i -> 实际高度）
const heights = ref<number[]>([]);
// 累计偏移（offsets[i] = 前 i 项总高度）
const offsets = ref<number[]>([0]);
// 数据
const data = shallowRef<any[]>([]);
const visibleCount = ref(0);
const startIndex = ref(0);
const endIndex = ref(0);
const offsetY = ref(0);
const totalHeight = computed(() => `${offsets.value[offsets.value.length - 1] || 0}px`);

/**
 * 二分查找：根据 scrollTop 快速定位起始索引
 */
function findStartIndex(scrollTop: number) {
  const arr = offsets.value;
  let lo = 0, hi = arr.length - 1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (arr[mid] < scrollTop) lo = mid + 1;
    else hi = mid - 1;
  }
  return Math.max(0, lo - 1);
}

/**
 * 某一项渲染后，用 ResizeObserver 测实际高度，更新 heights/offsets
 */
function measureAfterRender(entries: ResizeObserverEntry[]) {
  let changed = false;
  for (const en of entries) {
    const idx = Number((en.target as HTMLElement).dataset.index);
    if (!Number.isFinite(idx)) continue;
    const actual = en.contentRect.height;
    if (heights.value[idx] !== actual) {
      heights.value[idx] = actual;
      changed = true;
    }
  }
  if (changed) recalcOffsets();
}

function recalcOffsets() {
  const arr: number[] = [0];
  for (let i = 0; i < data.value.length; i++) {
    arr[i + 1] = arr[i] + (heights.value[i] ?? props.estimatedItemHeight);
  }
  offsets.value = arr;
}

// ... 滚动、加载等流程与定高版相同，核心差异在于：
// - 用 findStartIndex(scrollTop) 替代 Math.floor
// - 用 ResizeObserver 测量后再重算 offsets 与当前范围
</script>
```

### 5.6 与 Vue 3 生态结合的其他虚拟滚动方案

如果项目需要 **不定高 / 横向滚动 / 表格虚拟化 / 嵌套虚拟化** 等复杂场景，推荐直接使用成熟生态库，核心原理与本文一致：

| 库 | 特性 | 适用 |
|---|---|---|
| [`vue-virtual-scroller`](https://github.com/Akryum/vue-virtual-scroller) | 定高/不定高、水平垂直、回收池 | 通用场景，Vue 3 官方作者维护 |
| [`vue-virtual-scroll-list`](https://github.com/tangbc/vue-virtual-scroll-list) | 轻量、稳定、支持动态高度 | 长列表、聊天记录、表格行 |
| [`vxe-table`](https://xuliangzhan_admin.gitee.io/vxe-table) | 虚拟化表格 + 列/行 | 表格虚拟化（数据量大的后台表格） |

> **参考资料：**
> - Vue 3 — [组合式 API 文档](https://cn.vuejs.org/guide/extras/composition-api-faq.html)
> - MDN — [IntersectionObserver API](https://developer.mozilla.org/en-US/docs/Web/API/IntersectionObserver)
> - MDN — [ResizeObserver API](https://developer.mozilla.org/en-US/docs/Web/API/ResizeObserver)
> - Google Developers — [Rendering Performance](https://developers.google.com/web/fundamentals/performance/rendering)
> - CSS Triggers — [transform](https://csstriggers.com/transform)
