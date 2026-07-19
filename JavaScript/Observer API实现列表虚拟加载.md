# Observer API 实现列表虚拟加载

---

## 目录

1. [虚拟加载原理概述](#1-虚拟加载原理概述)
2. [核心机制详解](#2-核心机制详解)
3. [完整代码实现](#3-完整代码实现)
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

```javascript
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
function computeVisibleRange(scrollTop, itemHeight, visibleCount, bufferSize, totalItems) {
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

回收策略：每次滚动时，对比新旧索引范围，只更新变化的部分，而非全部重建。

---

## 3. 完整代码实现

### 3.1 虚拟列表核心类

```javascript
/**
 * VirtualList — 基于 Observer API 的虚拟列表实现
 *
 * 核心特性：
 *  - 仅渲染可视区域 + 缓冲区的 DOM 节点
 *  - 使用 IntersectionObserver 实现数据分片加载
 *  - 滚动事件防抖处理
 *  - DOM 节点复用，减少创建/销毁开销
 *  - 支持动态数据追加
 *
 * @example
 *   const list = new VirtualList({
 *     container: document.getElementById('list-container'),
 *     itemHeight: 50,
 *     bufferSize: 5,
 *     fetchData: async (offset, limit) => { ... }
 *   });
 */
class VirtualList {
    /**
     * @param {Object} options - 配置项
     * @param {HTMLElement} options.container      - 滚动容器元素
     * @param {number}       options.itemHeight    - 每项高度（px），需固定高度
     * @param {number}       [options.bufferSize=5] - 缓冲区大小（可视区上下各多渲染的项数）
     * @param {Function}     options.fetchData     - 数据获取函数 (offset, limit) => Promise<Array>
     * @param {number}       [options.pageSize=50] - 每次分片加载的数据条数
     * @param {Function}     [options.renderItem]  - 自定义渲染函数 (item, index) => HTMLElement
     * @param {number}       [options.debounceTime=16] - 防抖时间（ms），默认约 60fps
     */
    constructor(options) {
        // ---- 配置初始化 ----
        this.container = options.container;
        this.itemHeight = options.itemHeight;
        this.bufferSize = options.bufferSize ?? 5;
        this.fetchData = options.fetchData;
        this.pageSize = options.pageSize ?? 50;
        this.renderItem = options.renderItem ?? this.defaultRenderItem;
        this.debounceTime = options.debounceTime ?? 16;

        // ---- 状态管理 ----
        this.data = [];              // 全部已加载的数据
        this.totalItems = 0;         // 数据总条数（由服务端返回）
        this.isLoading = false;      // 是否正在加载数据
        this.hasMore = true;         // 是否还有更多数据

        // ---- 当前可见范围 ----
        this.currentStartIndex = -1;
        this.currentEndIndex = -1;

        // ---- 可渲染项数 ----
        this.visibleCount = 0;

        // ---- DOM 缓存（复用已创建的节点） ----
        this.itemPool = new Map();   // key: dataIndex, value: HTMLElement

        // ---- 构建 DOM 结构 ----
        this.buildDOM();

        // ---- 绑定方法 ----
        this.handleScroll = this.debounce(this.handleScroll.bind(this), this.debounceTime);
        this.handleIntersection = this.handleIntersection.bind(this);

        // ---- 初始化 ----
        this.init();
    }

    // ==================== DOM 构建 ====================

    /**
     * 构建列表的 DOM 骨架结构
     *
     * 结构：
     * <div class="virtual-list-container">        ← 滚动容器（用户传入）
     *   <div class="virtual-list-inner">          ← 内部撑高层（总高度 = totalItems * itemHeight）
     *     <div class="virtual-list-viewport">     ← 可视区域渲染层（通过 transform 定位）
     *       <!-- 实际渲染的列表项 -->
     *     </div>
     *   </div>
     *   <div class="virtual-list-sentinel">       ← 哨兵元素（IntersectionObserver 监听）
     *     <!-- 加载提示 -->
     *   </div>
     * </div>
     */
    buildDOM() {
        // 确保容器可以滚动
        this.container.style.overflow = 'auto';
        this.container.style.position = 'relative';

        // 内部撑高层：用于撑开滚动条，总高度 = 数据总量 * 单项高度
        this.innerWrapper = document.createElement('div');
        this.innerWrapper.className = 'virtual-list-inner';
        this.innerWrapper.style.position = 'relative';
        this.innerWrapper.style.height = '0px'; // 初始为 0，加载数据后更新

        // 可视区域渲染层：通过 transform: translateY() 定位到正确位置
        this.viewport = document.createElement('div');
        this.viewport.className = 'virtual-list-viewport';
        this.viewport.style.position = 'absolute';
        this.viewport.style.top = '0';
        this.viewport.style.left = '0';
        this.viewport.style.right = '0';
        this.viewport.style.willChange = 'transform'; // 提示浏览器开启 GPU 加速

        this.innerWrapper.appendChild(this.viewport);

        // 哨兵元素：用于 IntersectionObserver 触发加载更多
        this.sentinel = document.createElement('div');
        this.sentinel.className = 'virtual-list-sentinel';
        this.sentinel.style.height = '1px';
        this.sentinel.style.width = '100%';
        this.sentinel.innerHTML = '<div style="text-align:center;padding:10px;color:#999;">加载中...</div>';

        // 组装 DOM
        this.container.innerHTML = '';
        this.container.appendChild(this.innerWrapper);
        this.container.appendChild(this.sentinel);

        // 计算可视区域能容纳的项数
        this.visibleCount = Math.ceil(this.container.clientHeight / this.itemHeight) + this.bufferSize * 2;
    }

    // ==================== 初始化 ====================

    async init() {
        // 绑定滚动事件
        this.container.addEventListener('scroll', this.handleScroll, { passive: true });

        // 创建 IntersectionObserver 监听哨兵元素
        this.observer = new IntersectionObserver(this.handleIntersection, {
            root: this.container,           // 以滚动容器为视口
            rootMargin: '100px',            // 提前 100px 触发加载
            threshold: 0                    // 哨兵刚一出现就触发
        });
        this.observer.observe(this.sentinel);

        // 加载首批数据
        await this.loadMore();
    }

    // ==================== 数据加载 ====================

    /**
     * 加载更多数据（分片加载）
     * 由 IntersectionObserver 或首次初始化触发
     */
    async loadMore() {
        // 防止重复加载
        if (this.isLoading || !this.hasMore) return;

        this.isLoading = true;
        this.showSentinelLoading(true);

        try {
            // 调用外部数据获取函数
            const result = await this.fetchData(this.data.length, this.pageSize);

            // 兼容两种返回格式：
            //   { data: [...], total: 1000 }
            //   或直接返回数组 [...]
            if (Array.isArray(result)) {
                this.data.push(...result);
                this.totalItems = this.data.length; // 纯数组格式时，total 即当前长度
            } else {
                this.data.push(...result.data);
                this.totalItems = result.total;
            }

            // 判断是否还有更多数据
            this.hasMore = this.data.length < this.totalItems;

            // 更新内部撑高层高度
            this.updateTotalHeight();

            // 如果数据还很少（不足一屏），继续加载
            if (this.hasMore && this.data.length < this.visibleCount * 2) {
                this.isLoading = false;
                await this.loadMore();
                return;
            }

            // 首次渲染或更新可见区域
            if (this.currentStartIndex === -1) {
                this.renderVisibleItems(0);
            } else {
                // 重新计算当前可见范围（因为 totalHeight 可能变了）
                this.handleScroll();
            }

            // 如果数据已全部加载，隐藏哨兵
            if (!this.hasMore) {
                this.showSentinelLoading(false);
                this.showSentinelEnd();
            }

        } catch (error) {
            console.error('[VirtualList] 数据加载失败:', error);
            this.showSentinelError();
        } finally {
            this.isLoading = false;
        }
    }

    // ==================== 滚动处理 ====================

    /**
     * 滚动事件处理（经过防抖）
     * 计算新的可见范围，触发 DOM 更新
     */
    handleScroll() {
        if (this.data.length === 0) return;

        const scrollTop = this.container.scrollTop;
        const { startIndex, endIndex, offsetY } = this.computeVisibleRange(scrollTop);

        // 如果范围没有变化，跳过更新
        if (startIndex === this.currentStartIndex && endIndex === this.currentEndIndex) {
            return;
        }

        this.renderVisibleItems(offsetY, startIndex, endIndex);
    }

    /**
     * 计算当前可见的项索引范围
     *
     * @param {number} scrollTop - 当前滚动距离
     * @returns {{ startIndex: number, endIndex: number, offsetY: number }}
     */
    computeVisibleRange(scrollTop) {
        // 当前滚动位置对应的原始起始索引
        const rawStartIndex = Math.floor(scrollTop / this.itemHeight);

        // 起始索引：向上扩展缓冲区，不小于 0
        const startIndex = Math.max(0, rawStartIndex - this.bufferSize);

        // 结束索引：向下扩展缓冲区，不超过当前已加载数据量
        const endIndex = Math.min(
            this.data.length,
            rawStartIndex + this.visibleCount + this.bufferSize
        );

        // 渲染区域上方的偏移量
        const offsetY = startIndex * this.itemHeight;

        return { startIndex, endIndex, offsetY };
    }

    // ==================== DOM 渲染与回收 ====================

    /**
     * 渲染可见范围内的列表项
     *
     * 核心策略：增量更新 + DOM 复用
     *  - 移除不再可见的项
     *  - 保留仍然可见的项
     *  - 创建新出现的项
     *
     * @param {number} offsetY    - 渲染区域 Y 偏移量（用于 transform）
     * @param {number} startIndex - 起始索引
     * @param {number} endIndex   - 结束索引
     */
    renderVisibleItems(offsetY, startIndex, endIndex) {
        // 首次渲染时，startIndex 传入 0，endIndex 使用 visibleCount
        if (startIndex === undefined) {
            startIndex = 0;
            endIndex = Math.min(this.visibleCount, this.data.length);
            offsetY = 0;
        }

        this.currentStartIndex = startIndex;
        this.currentEndIndex = endIndex;

        // 1. 移除不再可见的 DOM 节点
        // 遍历 itemPool，找出不在 [startIndex, endIndex) 范围内的项并移除
        for (const [index, element] of this.itemPool) {
            const idx = Number(index);
            if (idx < startIndex || idx >= endIndex) {
                this.viewport.removeChild(element);
                this.itemPool.delete(index);
            }
        }

        // 2. 创建/复用可见范围内的 DOM 节点
        const fragment = document.createDocumentFragment();

        for (let i = startIndex; i < endIndex; i++) {
            if (this.itemPool.has(i)) {
                // 已存在，跳过（后续可能需要更新内容）
                continue;
            }

            const item = this.data[i];
            const element = this.renderItem(item, i);

            // 设置绝对定位：通过 top 值定位到正确位置
            // 注意：top 是相对于 viewport 的偏移，而非整个列表
            element.style.position = 'absolute';
            element.style.top = `${i * this.itemHeight}px`;
            element.style.left = '0';
            element.style.right = '0';
            element.style.height = `${this.itemHeight}px`;
            element.style.overflow = 'hidden';
            element.dataset.index = i;

            fragment.appendChild(element);
            this.itemPool.set(i, element);
        }

        // 批量插入新节点
        if (fragment.children.length > 0) {
            this.viewport.appendChild(fragment);
        }

        // 3. 通过 transform 将 viewport 平移到正确位置
        // 使用 transform 而非 top，因为 transform 触发 Composite 而非 Layout
        this.viewport.style.transform = `translateY(${offsetY}px)`;
    }

    // ==================== 工具方法 ====================

    /**
     * 更新内部撑高层的高度，使滚动条正确反映数据总量
     */
    updateTotalHeight() {
        this.innerWrapper.style.height = `${this.totalItems * this.itemHeight}px`;
    }

    /**
     * 默认的列表项渲染函数（可被外部覆盖）
     *
     * @param {Object} item  - 数据项
     * @param {number} index - 数据索引
     * @returns {HTMLElement}
     */
    defaultRenderItem(item, index) {
        const div = document.createElement('div');
        div.className = 'virtual-list-item';
        div.style.boxSizing = 'border-box';
        div.style.padding = '8px 12px';
        div.style.borderBottom = '1px solid #eee';
        div.style.backgroundColor = index % 2 === 0 ? '#f9f9f9' : '#fff';
        div.innerHTML = `
            <span style="color:#999;margin-right:8px;">#${index}</span>
            <span>${JSON.stringify(item)}</span>
        `;
        return div;
    }

    /**
     * 显示/隐藏哨兵加载状态
     */
    showSentinelLoading(show) {
        if (show) {
            this.sentinel.innerHTML = '<div style="text-align:center;padding:10px;color:#999;">加载中...</div>';
            this.sentinel.style.display = 'block';
        } else {
            this.sentinel.style.display = 'none';
        }
    }

    /**
     * 显示"已加载全部数据"提示
     */
    showSentinelEnd() {
        this.sentinel.innerHTML = '<div style="text-align:center;padding:10px;color:#ccc;">— 已加载全部数据 —</div>';
        this.sentinel.style.display = 'block';
    }

    /**
     * 显示加载错误提示
     */
    showSentinelError() {
        this.sentinel.innerHTML = `
            <div style="text-align:center;padding:10px;color:#f44336;">
                加载失败，
                <button onclick="this.closest('.virtual-list-sentinel').dispatchEvent(new CustomEvent('retry'))"
                        style="cursor:pointer;color:#1890ff;border:none;background:none;text-decoration:underline;">
                    点击重试
                </button>
            </div>`;
        this.sentinel.style.display = 'block';
    }

    /**
     * 防抖函数
     * 在连续触发的事件中，只执行最后一次
     *
     * @param {Function} fn    - 需要防抖的函数
     * @param {number}   delay - 防抖延迟（ms）
     * @returns {Function} 防抖后的函数
     */
    debounce(fn, delay) {
        let timer = null;
        return function(...args) {
            clearTimeout(timer);
            timer = setTimeout(() => {
                fn.apply(this, args);
            }, delay);
        };
    }

    /**
     * IntersectionObserver 回调
     * 哨兵元素进入视口时触发加载更多
     */
    handleIntersection(entries) {
        for (const entry of entries) {
            if (entry.isIntersecting) {
                this.loadMore();
            }
        }
    }

    // ==================== 公共方法 ====================

    /**
     * 重置列表（清空数据，重新加载）
     */
    reset() {
        this.data = [];
        this.totalItems = 0;
        this.hasMore = true;
        this.currentStartIndex = -1;
        this.currentEndIndex = -1;

        // 清空所有已渲染的 DOM 节点
        this.viewport.innerHTML = '';
        this.itemPool.clear();

        // 更新高度
        this.updateTotalHeight();

        // 重新加载
        this.loadMore();
    }

    /**
     * 滚动到指定索引的项
     *
     * @param {number} index - 目标索引
     */
    scrollToIndex(index) {
        const targetScrollTop = index * this.itemHeight;
        this.container.scrollTo({
            top: targetScrollTop,
            behavior: 'smooth'
        });
    }

    /**
     * 销毁实例，释放资源
     */
    destroy() {
        // 移除事件监听
        this.container.removeEventListener('scroll', this.handleScroll);

        // 断开 Observer
        if (this.observer) {
            this.observer.disconnect();
            this.observer = null;
        }

        // 清空 DOM
        this.container.innerHTML = '';
        this.itemPool.clear();
        this.data = [];
    }
}
```

### 3.2 使用示例

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Virtual List Demo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            padding: 20px;
            background: #f5f5f5;
        }

        .app {
            max-width: 600px;
            margin: 0 auto;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .app-header {
            padding: 16px 20px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .app-header h2 {
            font-size: 18px;
            color: #333;
        }

        .app-header .stats {
            font-size: 13px;
            color: #999;
        }

        /* 滚动容器 */
        .list-container {
            height: 500px;
            overflow-y: auto;
            overflow-x: hidden;
            background: #fff;
        }

        .list-container::-webkit-scrollbar {
            width: 6px;
        }

        .list-container::-webkit-scrollbar-thumb {
            background: #ccc;
            border-radius: 3px;
        }

        /* 撑高层 */
        .virtual-list-inner {
            position: relative;
            width: 100%;
        }

        /* 渲染层 */
        .virtual-list-viewport {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            will-change: transform;
        }

        /* 列表项 */
        .virtual-list-item {
            box-sizing: border-box;
            padding: 12px 16px;
            border-bottom: 1px solid #f0f0f0;
            display: flex;
            align-items: center;
            font-size: 14px;
            color: #333;
            transition: background-color 0.15s;
        }

        .virtual-list-item:hover {
            background-color: #e6f7ff !important;
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

        /* 哨兵 */
        .virtual-list-sentinel {
            text-align: center;
            padding: 12px;
            color: #999;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="app">
        <div class="app-header">
            <h2>虚拟列表示例</h2>
            <span class="stats" id="stats">已加载: 0 / 0</span>
        </div>

        <!-- 滚动容器 -->
        <div id="listContainer" class="list-container"></div>
    </div>

    <script src="./virtual-list.js"></script>
    <script>
        // ==================== 模拟服务端数据 ====================
        const TOTAL_ITEMS = 100000;
        const PAGE_SIZE = 50;

        /**
         * 模拟异步数据获取（模拟服务端分页接口）
         *
         * @param {number} offset - 偏移量
         * @param {number} limit  - 每页条数
         * @returns {Promise<{ data: Array, total: number }>}
         */
        function mockFetchData(offset, limit) {
            return new Promise((resolve) => {
                // 模拟网络延迟
                const delay = 300 + Math.random() * 200;
                setTimeout(() => {
                    const end = Math.min(offset + limit, TOTAL_ITEMS);
                    const items = [];
                    for (let i = offset; i < end; i++) {
                        items.push({
                            id: i,
                            name: `用户 ${String(i + 1).padStart(6, '0')}`,
                            email: `user${i + 1}@example.com`,
                            desc: `这是第 ${i + 1} 条数据的描述信息，用于展示虚拟列表的长文本截断效果。`,
                            avatar: String.fromCodePoint(65 + (i % 26)) // A-Z 循环
                        });
                    }
                    resolve({
                        data: items,
                        total: TOTAL_ITEMS
                    });
                }, delay);
            });
        }

        // ==================== 自定义渲染函数 ====================
        function customRenderItem(item, index) {
            const div = document.createElement('div');
            div.className = 'virtual-list-item';
            div.style.backgroundColor = index % 2 === 0 ? '#fafafa' : '#fff';

            div.innerHTML = `
                <div class="item-avatar">${item.avatar}</div>
                <div class="item-info">
                    <div class="item-name">${item.name}</div>
                    <div class="item-desc">${item.desc}</div>
                </div>
                <span class="item-index">#${index}</span>
            `;
            return div;
        }

        // ==================== 创建虚拟列表实例 ====================
        const container = document.getElementById('listContainer');
        const statsEl = document.getElementById('stats');

        const virtualList = new VirtualList({
            container: container,
            itemHeight: 60,         // 每项高度（含 padding + border）
            bufferSize: 5,          // 上下各缓冲 5 项
            pageSize: PAGE_SIZE,
            debounceTime: 16,       // ~60fps
            fetchData: mockFetchData,
            renderItem: customRenderItem
        });

        // 更新统计信息（定时轮询，仅用于演示）
        setInterval(() => {
            statsEl.textContent = `已加载: ${virtualList.data.length.toLocaleString()} / ${TOTAL_ITEMS.toLocaleString()} | 渲染DOM: ${virtualList.itemPool.size}`;
        }, 500);

        // 暴露到全局，方便调试
        window.virtualList = virtualList;
    </script>
</body>
</html>
```

---

## 4. 测试用例

### 4.1 单元测试

```javascript
/**
 * VirtualList 测试套件
 * 使用 console.assert 进行简单断言，可在浏览器控制台直接运行
 */

// 模拟 DOM 环境（Node.js 测试需要 jsdom，此处为浏览器内测试）
function createTestContainer() {
    const div = document.createElement('div');
    div.style.height = '400px';
    div.style.overflow = 'auto';
    document.body.appendChild(div);
    return div;
}

// 模拟数据获取
function mockFetch(offset, limit) {
    return Promise.resolve({
        data: Array.from({ length: limit }, (_, i) => ({ id: offset + i, text: `Item ${offset + i + 1}` })),
        total: 1000
    });
}

async function runTests() {
    console.log('='.repeat(60));
    console.log('VirtualList 测试套件');
    console.log('='.repeat(60));

    let passed = 0;
    let failed = 0;

    function assert(condition, message) {
        if (condition) {
            console.log(`  ✓ ${message}`);
            passed++;
        } else {
            console.error(`  ✗ ${message}`);
            failed++;
        }
    }

    // ---- 测试 1: 可见范围计算 ----
    console.log('\n[测试 1] computeVisibleRange 计算逻辑');

    const container = createTestContainer();
    const list = new VirtualList({
        container,
        itemHeight: 50,
        bufferSize: 3,
        fetchData: mockFetch,
        pageSize: 50
    });

    // 模拟已加载 100 条数据
    list.data = Array.from({ length: 100 }, (_, i) => ({ id: i }));
    list.totalItems = 1000;
    list.visibleCount = Math.ceil(400 / 50) + 3 * 2; // 8 + 6 = 14

    // scrollTop = 0
    let range = list.computeVisibleRange(0);
    assert(range.startIndex === 0, `scrollTop=0 时 startIndex 应为 0，实际: ${range.startIndex}`);
    assert(range.offsetY === 0, `scrollTop=0 时 offsetY 应为 0，实际: ${range.offsetY}`);

    // scrollTop = 500（第 10 项）
    range = list.computeVisibleRange(500);
    assert(range.startIndex === 7, `scrollTop=500 时 startIndex 应为 7（10-3 buffer），实际: ${range.startIndex}`);
    assert(range.offsetY === 350, `scrollTop=500 时 offsetY 应为 350（7*50），实际: ${range.offsetY}`);

    // scrollTop = 0 时 endIndex 不应超过数据量
    range = list.computeVisibleRange(0);
    assert(range.endIndex <= 100, `endIndex 不应超过已加载数据量 100，实际: ${range.endIndex}`);

    // ---- 测试 2: 防抖函数 ----
    console.log('\n[测试 2] 防抖（debounce）函数');

    let debounceCount = 0;
    const debouncedFn = list.debounce(() => { debounceCount++; }, 50);

    // 快速连续调用 10 次
    for (let i = 0; i < 10; i++) {
        debouncedFn();
    }

    assert(debounceCount === 0, '连续调用后立即检查，应尚未执行（延迟中）');

    await new Promise(resolve => setTimeout(resolve, 100));
    assert(debounceCount === 1, `延迟后应只执行 1 次，实际: ${debounceCount}`);

    // ---- 测试 3: DOM 渲染与回收 ----
    console.log('\n[测试 3] DOM 渲染与回收机制');

    // 手动注入数据以跳过异步加载
    list.data = Array.from({ length: 200 }, (_, i) => ({ id: i, text: `Item ${i}` }));
    list.totalItems = 1000;
    list.updateTotalHeight();

    // 渲染第一批
    list.renderVisibleItems(0, 0, 20);
    assert(list.itemPool.size === 20, `渲染 20 项后 itemPool.size 应为 20，实际: ${list.itemPool.size}`);
    assert(list.viewport.children.length === 20, `viewport 子节点数应为 20，实际: ${list.viewport.children.length}`);

    // 模拟滚动到新位置，渲染新范围
    list.renderVisibleItems(500, 10, 30);
    // 0-9 应被移除，10-19 保留，20-29 新增
    assert(list.itemPool.size === 20, `滚动后 itemPool.size 应为 20（10-29），实际: ${list.itemPool.size}`);

    // 检查索引 0-9 是否被移除
    for (let i = 0; i < 10; i++) {
        assert(!list.itemPool.has(i), `索引 ${i} 应已被回收`);
    }
    // 检查索引 10-29 是否存在
    for (let i = 10; i < 30; i++) {
        assert(list.itemPool.has(i), `索引 ${i} 应存在于 itemPool`);
    }

    // ---- 测试 4: 边界条件 ----
    console.log('\n[测试 4] 边界条件');

    // 空数据
    list.data = [];
    list.totalItems = 0;
    list.renderVisibleItems(0, 0, 0);
    assert(list.itemPool.size === 0, '空数据时 itemPool 应为空');

    // 数据少于可视区
    list.data = Array.from({ length: 3 }, (_, i) => ({ id: i }));
    list.totalItems = 3;
    list.renderVisibleItems(0, 0, 3);
    assert(list.itemPool.size === 3, '数据少于可视区时应全部渲染');

    // ---- 测试 5: 高度计算 ----
    console.log('\n[测试 5] 总高度计算');

    list.data = Array.from({ length: 100 }, (_, i) => ({ id: i }));
    list.totalItems = 1000;
    list.updateTotalHeight();
    assert(list.innerWrapper.style.height === '50000px', `总高度应为 50000px（1000*50），实际: ${list.innerWrapper.style.height}`);

    // ---- 测试 6: 性能验证 ----
    console.log('\n[测试 6] 渲染性能（DOM 节点数应远小于数据总量）');

    list.data = Array.from({ length: 500 }, (_, i) => ({ id: i }));
    list.totalItems = 10000;
    list.updateTotalHeight();

    const startTime = performance.now();
    list.renderVisibleItems(0, 0, 24); // 渲染 24 项（8 可见 + 上下各 8 缓冲）
    const endTime = performance.now();

    const renderTime = endTime - startTime;
    const domCount = list.itemPool.size;
    assert(domCount < 500, `DOM 节点数 ${domCount} 应远小于数据量 500`);
    assert(renderTime < 50, `渲染耗时 ${renderTime.toFixed(1)}ms 应 < 50ms`);

    console.log(`  → 渲染 ${domCount} 个 DOM 节点耗时: ${renderTime.toFixed(1)}ms`);

    // ---- 清理 ----
    list.destroy();
    document.body.removeChild(container);

    // ---- 总结 ----
    console.log('\n' + '='.repeat(60));
    console.log(`测试结果: 通过 ${passed} / 失败 ${failed}`);
    console.log('='.repeat(60));

    return { passed, failed };
}

// 运行测试
// runTests();
```

### 4.2 性能测试

```javascript
/**
 * 性能对比测试：虚拟列表 vs 普通列表
 */
async function performanceComparison() {
    console.log('='.repeat(60));
    console.log('性能对比：虚拟列表 vs 普通列表');
    console.log('='.repeat(60));

    const DATA_SIZE = 10000;
    const ITEM_HEIGHT = 50;
    const CONTAINER_HEIGHT = 400;

    // ---- 普通列表（全量渲染） ----
    console.log('\n[普通列表] 全量渲染 10,000 项...');

    const normalContainer = document.createElement('div');
    normalContainer.style.height = `${CONTAINER_HEIGHT}px`;
    normalContainer.style.overflow = 'auto';
    document.body.appendChild(normalContainer);

    const normalStart = performance.now();
    for (let i = 0; i < DATA_SIZE; i++) {
        const div = document.createElement('div');
        div.style.height = `${ITEM_HEIGHT}px`;
        div.textContent = `Item ${i}`;
        normalContainer.appendChild(div);
    }
    const normalEnd = performance.now();
    const normalTime = normalEnd - normalStart;
    const normalDOMCount = normalContainer.children.length;

    console.log(`  渲染耗时: ${normalTime.toFixed(1)}ms`);
    console.log(`  DOM 节点数: ${normalDOMCount}`);

    // 等待布局完成
    await new Promise(resolve => requestAnimationFrame(resolve));

    // 测试滚动性能
    const normalScrollStart = performance.now();
    normalContainer.scrollTop = 10000;
    await new Promise(resolve => requestAnimationFrame(resolve));
    normalContainer.scrollTop = 20000;
    await new Promise(resolve => requestAnimationFrame(resolve));
    normalContainer.scrollTop = 30000;
    await new Promise(resolve => requestAnimationFrame(resolve));
    const normalScrollEnd = performance.now();
    const normalScrollTime = normalScrollEnd - normalScrollStart;

    console.log(`  3 次滚动耗时: ${normalScrollTime.toFixed(1)}ms`);
    document.body.removeChild(normalContainer);

    // ---- 虚拟列表（按需渲染） ----
    console.log('\n[虚拟列表] 按需渲染 10,000 项...');

    const virtualContainer = document.createElement('div');
    virtualContainer.style.height = `${CONTAINER_HEIGHT}px`;
    virtualContainer.style.overflow = 'auto';
    document.body.appendChild(virtualContainer);

    const virtualStart = performance.now();
    const virtualList = new VirtualList({
        container: virtualContainer,
        itemHeight: ITEM_HEIGHT,
        bufferSize: 5,
        pageSize: 10000,
        fetchData: async (offset, limit) => {
            const end = Math.min(offset + limit, DATA_SIZE);
            return {
                data: Array.from({ length: end - offset }, (_, i) => ({ id: offset + i })),
                total: DATA_SIZE
            };
        }
    });

    // 等待数据加载和渲染
    await new Promise(resolve => setTimeout(resolve, 100));
    const virtualDOMCount = virtualList.itemPool.size;

    // 测试滚动性能
    const virtualScrollStart = performance.now();
    virtualContainer.scrollTop = 10000;
    await new Promise(resolve => requestAnimationFrame(resolve));
    virtualContainer.scrollTop = 20000;
    await new Promise(resolve => requestAnimationFrame(resolve));
    virtualContainer.scrollTop = 30000;
    await new Promise(resolve => requestAnimationFrame(resolve));
    const virtualScrollEnd = performance.now();
    const virtualScrollTime = virtualScrollEnd - virtualScrollStart;

    console.log(`  渲染 DOM 节点数: ${virtualDOMCount}`);
    console.log(`  3 次滚动耗时: ${virtualScrollTime.toFixed(1)}ms`);

    // ---- 对比结果 ----
    console.log('\n' + '='.repeat(60));
    console.log('对比结果:');
    console.log(`  DOM 节点数:  普通 ${normalDOMCount}  vs  虚拟 ${virtualDOMCount}  (减少 ${((1 - virtualDOMCount / normalDOMCount) * 100).toFixed(1)}%)`);
    console.log(`  滚动性能:    普通 ${normalScrollTime.toFixed(1)}ms  vs  虚拟 ${virtualScrollTime.toFixed(1)}ms`);
    console.log('='.repeat(60));

    virtualList.destroy();
    document.body.removeChild(virtualContainer);
}

// 运行性能对比
// performanceComparison();
```

### 4.3 快速滚动压力测试

```javascript
/**
 * 快速滚动压力测试
 * 验证快速滚动时不会出现白屏、错位、或卡顿
 */
async function stressTest() {
    console.log('='.repeat(60));
    console.log('快速滚动压力测试');
    console.log('='.repeat(60));

    const container = document.createElement('div');
    container.style.height = '400px';
    container.style.overflow = 'auto';
    document.body.appendChild(container);

    const list = new VirtualList({
        container,
        itemHeight: 50,
        bufferSize: 3,
        pageSize: 100,
        fetchData: async (offset, limit) => ({
            data: Array.from({ length: limit }, (_, i) => ({
                id: offset + i,
                text: `Item ${offset + i + 1}`
            })),
            total: 10000
        })
    });

    // 等待初始加载
    await new Promise(resolve => setTimeout(resolve, 500));

    // 模拟快速滚动
    const scrollPositions = [
        0, 500, 1500, 3000, 6000, 10000, 20000, 35000, 50000,
        80000, 120000, 180000, 250000, 350000, 450000
    ];

    let errors = 0;
    const startTime = performance.now();

    for (const pos of scrollPositions) {
        container.scrollTop = pos;

        // 等待渲染
        await new Promise(resolve => requestAnimationFrame(resolve));

        // 验证：渲染区域的位置是否与滚动位置匹配
        const transform = list.viewport.style.transform;
        const match = transform.match(/translateY\((\d+)px\)/);
        if (match) {
            const translateY = parseInt(match[1]);
            const expectedOffset = list.currentStartIndex * list.itemHeight;

            if (Math.abs(translateY - expectedOffset) > 5) {
                console.error(`  位置错位: scrollTop=${pos}, translateY=${translateY}, expected=${expectedOffset}`);
                errors++;
            }
        }

        // 验证：渲染的 DOM 节点数是否合理
        const domCount = list.itemPool.size;
        const expectedMax = list.visibleCount + list.bufferSize;
        if (domCount > expectedMax * 2) {
            console.error(`  DOM 节点过多: ${domCount} > ${expectedMax * 2}`);
            errors++;
        }
    }

    const endTime = performance.now();
    const totalTime = endTime - startTime;

    console.log(`  滚动位置数: ${scrollPositions.length}`);
    console.log(`  总耗时: ${totalTime.toFixed(1)}ms`);
    console.log(`  平均耗时: ${(totalTime / scrollPositions.length).toFixed(1)}ms/次`);
    console.log(`  错误数: ${errors}`);

    if (errors === 0) {
        console.log('  结果: 通过 — 快速滚动无异常');
    } else {
        console.error(`  结果: 失败 — ${errors} 个错误`);
    }

    list.destroy();
    document.body.removeChild(container);
}

// 运行压力测试
// stressTest();
```

---

## 5. 性能优化与注意事项

### 5.1 优化策略总结

| 优化点 | 实现方式 | 预期效果 |
|--------|----------|----------|
| **DOM 节点数控制** | 只渲染可见区域 + 缓冲区 | 10,000 条数据仅渲染 ~20 个 DOM 节点 |
| **防抖滚动事件** | `debounce(fn, 16ms)` ≈ 60fps | 避免高频触发渲染，减少不必要的计算 |
| **增量更新** | 对比新旧范围，只更新变化项 | 避免全量重建 DOM |
| **DocumentFragment** | 批量插入新节点 | 减少回流次数 |
| **GPU 加速** | `will-change: transform` + `translateY` | 定位操作只触发 Composite，不触发 Layout |
| **IntersectionObserver** | 异步触发数据加载 | 不阻塞主线程，性能优于 scroll 事件检测 |
| **passive 事件** | `{ passive: true }` | 告知浏览器不会调用 `preventDefault`，提升滚动流畅度 |
| **WeakMap 缓存** | 可选，用于缓存 DOM 关联数据 | 自动 GC，避免内存泄漏 |

### 5.2 GPU 加速原理

```
传统方式（top / marginTop）：
  scroll → 修改 top → 触发 Layout → 触发 Paint → 触发 Composite

优化方式（transform）：
  scroll → 修改 transform → 直接触发 Composite（跳过 Layout 和 Paint）
```

### 5.3 注意事项

1. **固定高度约束**：本实现假设每项高度固定。若需支持不定高，需使用 `ResizeObserver` 动态测量每项实际高度，并维护一个高度累加数组用于计算偏移量。

2. **数据一致性**：`totalItems` 应与服务端保持一致。若数据在滚动过程中被修改（增删），需重新计算 `totalHeight` 和当前可见范围。

3. **缓冲区大小**：过小会导致快速滚动时出现白屏；过大会增加不必要的 DOM 节点。建议设置为可视区能容纳项数的 0.5~1 倍。

4. **IntersectionObserver 兼容性**：IE 不支持，需要使用 polyfill 或降级为 scroll 事件检测。

5. **SSR 兼容**：虚拟列表依赖浏览器 DOM API，服务端渲染时需特殊处理或使用客户端动态加载。

### 5.4 扩展到不定高列表

```javascript
// 不定高虚拟列表的关键数据结构
class DynamicHeightVirtualList extends VirtualList {
    constructor(options) {
        super(options);
        // 维护每项的实际高度
        this.itemHeights = new Map();    // index → 实际高度
        // 维护每项的累计偏移量（用于快速计算位置）
        this.offsets = [];               // offsets[i] = 前 i 项的总高度
        // 默认预估高度
        this.estimatedItemHeight = options.estimatedItemHeight ?? 50;
    }

    /**
     * 二分查找：根据 scrollTop 快速定位起始索引
     */
    findStartIndex(scrollTop) {
        let low = 0;
        let high = this.offsets.length - 1;

        while (low <= high) {
            const mid = Math.floor((low + high) / 2);
            if (this.offsets[mid] < scrollTop) {
                low = mid + 1;
            } else {
                high = mid - 1;
            }
        }
        return Math.max(0, low - 1);
    }

    // 使用 ResizeObserver 在渲染后测量实际高度，更新 offsets 数组
    // ...（完整实现省略，原理相同）
}
```

---

> **参考资料：**
> - MDN — [IntersectionObserver API](https://developer.mozilla.org/en-US/docs/Web/API/IntersectionObserver)
> - MDN — [ResizeObserver API](https://developer.mozilla.org/en-US/docs/Web/API/ResizeObserver)
> - web.dev — [Virtualize large lists with react-window](https://web.dev/virtualize-long-lists-react-window/)
> - Google Developers — [Rendering Performance](https://developers.google.com/web/fundamentals/performance/rendering)
> - CSS Triggers — [transform](https://csstriggers.com/transform)