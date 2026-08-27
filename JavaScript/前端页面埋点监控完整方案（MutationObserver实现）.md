# 前端页面埋点监控完整方案（MutationObserver 实现）

> 文档主题：以浏览器原生 **MutationObserver** 为核心的前端埋点监控工程方案。
>
> 核心能力：通过 MO 监听 DOM 树动态变化，自动识别带 `data-track-*` 属性的元素、匹配配置化 CSS Selector 规则，无需每处组件手动写 Vue 指令或 React Hook，即可实现对异步渲染列表、动态路由、第三方组件的零代码/低代码埋点。

---

## 目录

- [前端页面埋点监控完整方案（MutationObserver 实现）](#前端页面埋点监控完整方案mutationobserver-实现)
  - [目录](#目录)
  - [一、方案定位与技术背景](#一方案定位与技术背景)
    - [1.1 为什么引入 MutationObserver？](#11-为什么引入-mutationobserver)
    - [1.2 MO 方案 vs 手动指令/Hook 方案对比](#12-mo-方案-vs-手动指令hook-方案对比)
    - [1.3 适用场景与不适用边界](#13-适用场景与不适用边界)
  - [二、整体架构设计](#二整体架构设计)
    - [2.1 四层架构与 MO 接入点](#21-四层架构与-mo-接入点)
    - [2.2 数据流向全景（MO 自动绑定链路）](#22-数据流向全景mo-自动绑定链路)
    - [2.3 技术选型推荐](#23-技术选型推荐)
  - [三、埋点分类与数据规范](#三埋点分类与数据规范)
    - [3.1 三类埋点（MO 增强版）](#31-三类埋点mo-增强版)
    - [3.2 TrackingEvent 通用数据结构](#32-trackingevent-通用数据结构)
    - [3.3 data-track-\* 属性规范](#33-data-track--属性规范)
    - [3.4 埋点规则 DSL（CSS Selector + 属性双通道）](#34-埋点规则-dslcss-selector--属性双通道)
  - [四、MutationObserver 采集 SDK 完整实现](#四mutationobserver-采集-sdk-完整实现)
    - [4.1 SDK 模块架构](#41-sdk-模块架构)
    - [4.2 TypeScript 核心骨架](#42-typescript-核心骨架)
    - [4.3 MutationObserver 自动埋点引擎](#43-mutationobserver-自动埋点引擎)
    - [4.4 data-track 属性点击/曝光自动绑定](#44-data-track-属性点击曝光自动绑定)
    - [4.5 配置化 CSS Selector 规则埋点（零代码模式）](#45-配置化-css-selector-规则埋点零代码模式)
    - [4.6 MO + IntersectionObserver 联动曝光](#46-mo--intersectionobserver-联动曝光)
    - [4.7 去重绑定与性能控制](#47-去重绑定与性能控制)
    - [4.8 动态路由与 SPA 组件卸载清理](#48-动态路由与-spa-组件卸载清理)
  - [五、埋点配置化管理平台](#五埋点配置化管理平台)
    - [5.1 规则管理平台架构](#51-规则管理平台架构)
    - [5.2 规则动态下发与灰度发布](#52-规则动态下发与灰度发布)
    - [5.3 可视化规则生成（Chrome 插件点选）](#53-可视化规则生成chrome-插件点选)
  - [六、服务端处理与存储](#六服务端处理与存储)
    - [6.1 Fastify 网关：限流、补维、写入 Kafka](#61-fastify-网关限流补维写入-kafka)
    - [6.2 数据清洗与脱敏](#62-数据清洗与脱敏)
    - [6.3 ClickHouse 建表语句](#63-clickhouse-建表语句)
  - [七、看板、告警、性能与合规](#七看板告警性能与合规)
    - [7.1 三类 Grafana 看板设计](#71-三类-grafana-看板设计)
    - [7.2 Prometheus 四级告警规则](#72-prometheus-四级告警规则)
    - [7.3 MO 对主线程的占用控制](#73-mo-对主线程的占用控制)
    - [7.4 隐私合规（个保法/GDPR）](#74-隐私合规个保法gdpr)
  - [八、实施落地与面试题集](#八实施落地与面试题集)
    - [8.2 MO 埋点常见问题排查手册](#82-mo-埋点常见问题排查手册)
    - [8.3 前端埋点监控面试题（MutationObserver 专题）](#83-前端埋点监控面试题mutationobserver-专题)
  - [参考资料](#参考资料)

---

## 一、方案定位与技术背景

### 1.1 为什么引入 MutationObserver？

传统前端埋点依赖 Vue 指令、React Hook 等手动绑定方式，在以下场景中暴露明显痛点：

- **异步渲染列表**：商品瀑布流、虚拟滚动、分页等场景，组件反复 mount/unmount，指令/Hook 需要组件方手动维护 `observe/unobserve`，容易遗漏导致曝光不采集、点击重复采集。
- **第三方/遗留组件**：引入的 UI 库（ElementPlus AntD）、历史遗留 jQuery 代码、后端模板渲染的 DOM，无法或不方便直接插入 v-track 或 onClick 埋点钩子。
- **配置化零代码**：业务方希望产品/运营同学在后台配置"搜索框按钮点击率"、"第 N 张 Banner 曝光量"，不经过前端发版即可生效，手动埋点做不到。

**MutationObserver（DOM 树变化监听器）** 它能监听整个文档树的节点增删、属性变化、子树结构调整，配合稳定的 CSS Selector 或 `data-track-*` 属性约定，可在任何 DOM 出现的瞬间自动完成埋点绑定——这就是"自动埋点 / 零代码埋点"的技术基础。

### 1.2 MO 方案 vs 手动指令/Hook 方案对比

| 维度 | **MutationObserver 自动埋点** | Vue/React 手动指令/Hook |
|------|-----------------------------|-----------------------|
| 接入方式 | **零代码**：埋点平台下发规则 OR 约定 `data-track-*` 属性 | 每处交互必须加指令/Hook |
| 动态 DOM 支持 | ✅ 天生支持（MO 监听新增节点即自动绑定） | ⚠️ 需要手动维护 observe/unobserve |
| 第三方组件支持 | ✅ 只需目标 DOM 有稳定选择器或属性 | ❌ 无法直接侵入内部 |
| 配置化能力 | ✅ 规则 JSON 下发，无需发版 | ❌ 必须代码改 + 发版 |
| 性能开销 | 需谨慎配置（子树扫描、匹配选择器耗时） | 低（直接事件绑定） |
| 调试复杂度 | 中（需理解 MO 回调与选择器匹配链路） | 低（代码断点直观） |
| 推荐定位 | 常规曝光/点击埋点 80% 覆盖 | 核心业务链路 20% 强语义埋点 |

**最佳实践**：二者并不互斥。MO 自动化覆盖 80% 常规场景，手动埋点覆盖 20% 核心业务流程，两者共用同一 SDK 底座与服务端链路。

### 1.3 适用场景与不适用边界

**适用**：
1. 电商列表、Banner、推荐位：元素数量大、变化频繁、UI 迭代快
2. 运营活动页：每周上线多个活动，埋点零代码化可节省 60% 前端工时
3. 中台/遗留系统：多团队协作、代码规范不统一，强制 data-track-* 约定 + MO 自动绑定比代码 review 更可靠
4. 数据实验：A/B 测试新增的模块埋点，无需跟随代码发版

**不适用**：
1. 极高频 DOM 变化场景（每秒 > 1000 次 mutation）：MO 回调会累积导致主线程卡顿，需切换手动模式
2. 涉及精确计算、金额风控级别的强语义埋点（如支付成功）：必须用代码手动埋点，避免配置错误导致数据口径不准
3. 复杂上下文采集（如 `_mouse.x/y`、组件内 state 字段）：data-track-* 需要把值渲染到 DOM，MO 才能读到；不如直接在代码里 track

---

## 二、整体架构设计

### 2.1 四层架构与 MO 接入点

```
┌────────────────────────────────────────────────────────────────────────┐
│  层 4：消费层                                                            │
│  Grafana 看板 ｜ 漏斗/留存 ｜ Prometheus 告警 ｜ 埋点配置管理平台          │
└─────────────────────────────────────┬──────────────────────────────────┘
                                      │ SQL/PromQL/规则下发
┌─────────────────────────────────────┴──────────────────────────────────┐
│  层 3：存储层                                                            │
│  ClickHouse MergeTree + SummingMergeTree 聚合视图 ｜ Redis BloomFilter  │
│  Kafka（事件队列 + 规则下发队列） ｜ MySQL（规则元数据 + 版本 + 审批）   │
└─────────────────────────────────────┬──────────────────────────────────┘
                                      │ HTTPS Beacon / 规则 CDN JSON
┌─────────────────────────────────────┴──────────────────────────────────┐
│  层 2：接入层                                                            │
│  Fastify 网关（限流 + 签名 + IP/UA 补维 + 布隆去重 + Kafka Produce）   │
│  规则 CDN：埋点规则 JSON <event, selector, props_map> + ETag 缓存       │
└─────────────────────────────────────┬──────────────────────────────────┘
                                      │ ← 浏览器
┌─────────────────────────────────────┴──────────────────────────────────┐
│  层 1：采集层（SDK，MutationObserver 为核心）                             │
│  ┌──────────────────────┐                                               │
│  │ MutationObserver 引擎 │← ① DOM 树新增/属性变化触发回调                │
│  │  · 子树全量扫描       │  ② 匹配 data-track-* 属性                     │
│  │  · CSS Selector 匹配 │  ③ 匹配配置中心下发的埋点规则                  │
│  │  · 去重绑定 WeakMap  │→ ④ 触发后交给 Queue 批量上报                   │
│  └──────────┬───────────┘                                               │
│             ▼                                                           │
│  EventQueue(20条/5s批量 sendBeacon)  +  IdentityManager                 │
│  IntersectionObserver(曝光)  +  WebVitals  +  JSErrorCollector          │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流向全景（MO 自动绑定链路）

```
浏览器 DOM 变化
  │
  ├─ 新节点挂载 ─────────┐
  ├─ data-track-* 属性变 ┤── MutationObserver callback (batch, rAF 节流)
  └─ 节点删除           │      │
                        └──────▼─────────────────────────────┐
                               │   遍历新增节点 + 子节点 descendant  │
                               │   ▼                           │
                      ┌────────┴──────────┐                  │
                      │ 匹配 data-track-* │ → 解析事件名与props  │
                      └────────┬──────────┘                  │
                               │                              │
                               │   ┌────────────────────┐    │
                               └─→ │ 匹配 CSS Selector 规则│ → 配置中心下发命中  │
                                   └────────┬───────────┘    │
                                            │                │
                                            ▼                │
                              ┌─────────────────────────┐    │
                              │ 去重绑定：WeakSet.has(el)?│    │
                              │   YES → 跳过              │    │
                              │   NO → addEventListener   │    │
                              │         + IO.observe(曝光)│    │
                              └────────────────┬────────┘    │
                                               │             │
                                               ▼             │
                        点击事件 → track(click_xxx)   曝光事件 → track(show_xxx)
                                               │
                                               ▼
                          EventQueue(20条 or 5s or 页面卸载)
                                               │
                                               ▼
                        navigator.sendBeacon → Fastify 网关 → Kafka → ClickHouse
```

### 2.3 技术选型推荐

| 模块 | 技术 | 选型理由 |
|------|-----|---------|
| **核心自动化引擎** | MutationObserver | 监听 DOM 变化，原生 API，零运行时依赖 |
| **曝光联动** | MutationObserver + IntersectionObserver | MO 发现节点 → 交给 IO 判断是否在视口 |
| **埋点规则存储** | MySQL + Nacos/CDN JSON | 版本管理 + 审批流 + 边缘缓存秒级下发 |
| **采集 SDK** | TypeScript 自研 25KB gzip | Tree-shaking + 插件体系 + MO 引擎可选装 |
| **网关** | Fastify 4 | 比 Express 高 2~3 倍吞吐，TypeBox 类型校验 |
| **消息队列** | Kafka 3.x | 百万级 QPS、多分区保序、死信队列 |
| **存储** | ClickHouse 24.x | 列存 + 分区 + 预聚合，亿级数据秒查 |
| **监控告警** | Prometheus + Grafana + Alertmanager | 成熟开源生态，四级告警飞书/电话通知 |
| **可视化规则生成** | Chrome 扩展 | 业务同学点选元素，自动生成稳定 CSS Selector |

---

## 三、埋点分类与数据规范

### 3.1 三类埋点（MO 增强版）

| 类型 | 前缀 | 示例 | MO 采集方式 |
|------|-----|------|------------|
| **曝光** | `show_xxx` | `show_banner_1` | MO 匹配节点 → 加入 IO.observe → 视口比例+时长达标触发 |
| **点击** | `click_xxx` | `click_search_button` | MO 匹配节点 → addEventListener('click', capture) |
| **属性变化** | `attr_xxx` | `attr_like_status_change` | MO attributes 模式 → data-track-value 变化时触发 |
| **页面访问** | `page_xxx` | `page_product_detail` | RouterPlugin 路由钩子（MO 不便监听 history 变化） |
| **业务流程** | `evt_xxx` | `evt_pay_success` | 代码手动埋点（MO 不参与，属风控级强语义） |

### 3.2 TrackingEvent 通用数据结构

```typescript
export interface TrackingEvent {
  // 基础
  event: string;
  event_id: string;        // uuid
  timestamp: number;
  event_version: string;
  source: 'manual' | 'data-track' | 'selector-rule' | 'attr-change' | 'auto';  // MO 新增字段：来源溯源

  // 身份
  user_id?: string;
  anonymous_id: string;
  distinct_id: string;
  login_status: 'logged' | 'guest';

  // 设备与环境
  platform: 'web' | 'h5';
  os: string;
  browser: string;
  screen_resolution: string;
  network_type: string;

  // 页面
  page_path: string;
  page_referrer: string;
  ab_test_group?: string;

  // 会话
  session_id: string;
  session_event_index: number;

  // MO 特有：元素定位与规则信息（用于排查"为什么这个按钮没采到"）
  _track?: {
    rule_id?: string;          // 命中哪条配置规则（UUID）
    rule_version?: string;     // 规则版本号，方便回滚定位
    selector_matched?: string; // 命中的 CSS Selector（如果是规则模式）
    data_track_attrs?: Record<string, string>; // 完整的 data-track-* 属性快照
    dom_path?: string;         // 稳定 xpath/css 路径，回放用
    mount_seq?: number;        // 同 selector 第几个命中（用于 banner_1 / banner_2 排序）
  };

  properties: Record<string, any>;
}
```

### 3.3 data-track-* 属性规范

**属性命名约定（驼峰的 DOM 属性会被浏览器自动小写，因此规范统一使用短横线分隔，读取时用 dataset.驼峰）**

| HTML 属性 | 对应 dataset.xxx | 必填 | 示例 | 说明 |
|----------|-----------------|-----|------|------|
| `data-track-event` | `trackEvent` | ✅ | `click_add_to_cart` | 事件名，大小写蛇形 |
| `data-track-props` | `trackProps` | ⚠️ | `{"sku_id":"s1","price":9900}` | JSON 字符串（复杂属性场景） |
| `data-track-<key>` | `track<Key>` | ✅ | `data-track-sku-id="s1"` | 单字段 props 替代 JSON，可读性更好 |
| `data-track-on` | `trackOn` | 推荐 | `click|exposure` / `click` / `attr` | 声明该节点需要采集哪些事件，不写默认 click+exposure |
| `data-track-exposure-ratio` | `trackExposureRatio` | 推荐 | `0.5` | 覆盖全局 50% 阈值 |
| `data-track-once` | `trackOnce` | 推荐 | `true` | 曝光只采一次，默认 true |
| `data-track-bind-id` | `trackBindId` | 自动 | `<uuid>` | SDK 自动注入，用于去重绑定的 WeakMap key |

**使用示例**

```html
<!-- 方案 A：单属性写法（推荐，语义清晰） -->
<button
  data-track-event="click_add_to_cart"
  data-track-sku-id="SKU001"
  data-track-price="9900"
  data-track-recommend-source="banner"
  data-track-on="click"
>加入购物车</button>

<!-- 方案 B：props 合并 JSON（字段多时避免属性过多） -->
<div
  data-track-event="show_product_card"
  data-track-props='{"sku_id":"SKU001","category":"手机"}'
  data-track-on="exposure"
  data-track-exposure-ratio="0.8"
  class="product-card"
></div>

<!-- 方案 C：属性变化埋点（like 状态切换） -->
<like-button
  data-track-event="attr_like_status_change"
  data-track-on="attr"
  data-track-liked="false"
></like-button>
```

### 3.4 埋点规则 DSL（CSS Selector + 属性双通道）

MO + 配置化埋点时下发的规则 JSON 结构：

```typescript
export interface TrackRule {
  rule_id: string;                   // UUID
  version: string;                   // 版本，如 1.2.0
  owner: string;                     // 负责人（飞书告警@人）
  event: string;                     // 事件名
  event_version: string;             // 事件版本

  // ===== 匹配方式 =====
  scope_selector?: string;           // 限定匹配范围（.page-home .banner-list 内）
  element_selector: string;          // 必选：目标元素 CSS Selector
  attr_filter?: {                    // 属性过滤：除了 selector，还得满足 data-track-* = value
    [key: string]: string | RegExp | null;
  };
  mount_index?: number | [number, number]; // 只取第 N 个，或 [start, end) 区间

  // ===== 采集类型 =====
  collect: Array<'click' | 'exposure' | 'attr'>;

  // ===== 曝光参数 =====
  exposure_ratio?: number;           // 默认 0.5
  exposure_min_duration_ms?: number; // 默认 1000
  exposure_once?: boolean;           // 默认 true

  // ===== 属性采集：从 DOM 读取哪些值注入 properties
  props_map: {
    [target_key: string]:
      | { type: 'text'; selector?: string; slice?: [number, number] }
      | { type: 'attr'; name: string; attr_selector?: string }
      | { type: 'dataset'; name: string }
      | { type: 'constant'; value: string | number | boolean }
      | { type: 'mount_seq'; start?: number }; // 第 N 个命中
  };

  // ===== 属性变化触发：当哪几个 dataset 属性变化时才上报 collect=attr 场景 =====
  attr_watch?: string[];             // ['liked', 'selected']

  // ===== 执行熔断（防卡死页面） =====
  max_matches_per_scope?: number;    // 默认 200，单页面同规则命中不超过 200 个
  callback_deadline_ms?: number;     // 默认 3，单元素回调超过 3ms 熔断此规则
}
```

---

## 四、MutationObserver 采集 SDK 完整实现

### 4.1 SDK 模块架构

```
TrackingSDK
├── API: track() / login() / logout() / forceFlush()
├── EventQueue + RequestManager (sendBeacon/fetch/IndexedDB)
├── IdentityManager + ContextCollector
├── WebVitalsPlugin + JSErrorPlugin + RouterPlugin
│
└── 核心：AutoTrackEngine（MutationObserver 底座）
    ├── 1. MutationObserver 回调 + rAF 批量合并
    ├── 2. DataTrackBinding：扫描 data-track-* 绑定点击/曝光
    ├── 3. SelectorRuleBinding：匹配下发 Selector 规则 + 采集 properties
    ├── 4. AttrChangeBinding：属性变化触发埋点
    ├── 5. ExposureManager：MO 发现节点 → IO.observe → 达标触发
    ├── 6. Deduplicator：WeakMap(el → rule_id[] ) 防重复绑定
    └── 7. Throttler/Fuse：单页面命中超过阈值 → 熔断 + 上报告警
```

### 4.2 TypeScript 核心骨架

```typescript
// sdk/src/core/sdk.ts
import { EventQueue } from './event-queue';
import { IdentityManager } from './identity';
import { ContextCollector } from './context';
import { RequestManager } from './request';
import { AutoTrackEngine } from './auto-track/engine';
import type { TrackingEvent, TrackRule } from './types';

export interface TrackingSDKOptions {
  endpoint: string;
  app_id: string;
  app_version: string;
  sampleRate?: number;
  debug?: boolean;
  batchSize?: number;
  flushInterval?: number;
  /** 自动化埋点配置 */
  autoTrack?: {
    enableDataTrackAttr?: boolean;      // 启用 data-track-* 自动扫描（默认 true）
    enableSelectorRules?: boolean;      // 启用配置中心规则（默认 true）
    rulesCDNUrl?: string;               // 规则 JSON CDN 地址
    root?: Element | Document;          // 观察根，默认 document
    subtree?: boolean;                  // 默认 true，深度遍历
    performanceMode?: 'balanced' | 'performance-first' | 'accuracy-first';
    maxMutationsPerFrame?: number;      // 每帧处理 mutation 上限
  };
}

export class TrackingSDK {
  private static _i: TrackingSDK | null = null;
  static get i() { return TrackingSDK._i!; }

  public queue: EventQueue;
  public identity: IdentityManager;
  public ctx: ContextCollector;
  public autoTrack?: AutoTrackEngine;

  constructor(private opts: Required<TrackingSDKOptions>) {
    TrackingSDK._i = this;
    this.queue = new EventQueue({
      maxSize: opts.batchSize ?? 20,
      onFlush: (batch) => new RequestManager({ endpoint: opts.endpoint, app_id: opts.app_id }).sendBatch(batch),
    });
    this.identity = new IdentityManager();
    this.ctx = new ContextCollector();
  }

  async start() {
    this.queue.startAutoFlush(this.opts.flushInterval ?? 5000);
    // MO 引擎初始化
    if (this.opts.autoTrack) {
      this.autoTrack = new AutoTrackEngine(this, this.opts.autoTrack);
      await this.autoTrack.init();
      this.autoTrack.observe(this.opts.autoTrack.root ?? document);
    }
    this.track('page_app_launch', {}, { source: 'auto' });
  }

  /** 对外唯一 track 入口 */
  track(
    event: string,
    properties: Record<string, any> = {},
    extras: Partial<Pick<TrackingEvent, 'source' | '_track'>> = {}
  ) {
    if (Math.random() > (this.opts.sampleRate ?? 1)) return;
    const ctx = this.ctx.collect();
    const evt: TrackingEvent = {
      event,
      event_id: crypto.randomUUID?.() ?? 'ev_' + Math.random().toString(36),
      timestamp: Date.now(),
      event_version: this.ctx.eventVersionOf(event),
      source: extras.source ?? 'manual',
      user_id: this.identity.getUserId() ?? undefined,
      anonymous_id: this.identity.getAnonymousId(),
      distinct_id: this.identity.getDistinctId(),
      login_status: this.identity.getLoginStatus(),
      ...ctx,
      session_id: this.identity.getSessionId(),
      session_event_index: this.identity.nextSessionIndex(),
      _track: extras._track,
      properties,
    };
    if (this.opts.debug) console.log('[track:%c%s%c]', 'color:#2ea043', event, '', evt);
    this.queue.push(evt);
  }
}
```

### 4.3 MutationObserver 自动埋点引擎

**核心思路**：MO 回调本身非常频繁（快速渲染列表一次会触发上百条 mutation record），必须用 `requestAnimationFrame` 做帧级合并，只在每帧结束时一次性扫描所有"脏根节点"。

```typescript
// sdk/src/auto-track/engine.ts
import type { TrackingSDK } from '../core/sdk';
import type { TrackRule } from '../types';
import { DataTrackBinding } from './data-track-binding';
import { SelectorRuleBinding } from './selector-rule-binding';
import { AttrChangeBinding } from './attr-change-binding';
import { ExposureManager } from './exposure-manager';
import { Deduplicator } from './deduplicator';

export interface AutoTrackOptions {
  enableDataTrackAttr?: boolean;
  enableSelectorRules?: boolean;
  rulesCDNUrl?: string;
  root?: Element | Document;
  subtree?: boolean;
  performanceMode?: 'balanced' | 'performance-first' | 'accuracy-first';
  maxMutationsPerFrame?: number;
}

export class AutoTrackEngine {
  private mo: MutationObserver | null = null;
  private dirtyRoots: Set<Node> = new Set();  // 帧级脏节点集合
  private rafId: number | null = null;
  private stopSignal = false;

  rules: TrackRule[] = [];
  deduplicator: Deduplicator;
  dataTrack: DataTrackBinding;
  selectorRule: SelectorRuleBinding;
  attrChange: AttrChangeBinding;
  exposure: ExposureManager;
  fuseRulesBroken = new Set<string>();  // 熔断的 rule_id

  constructor(
    private sdk: TrackingSDK,
    private opts: Required<AutoTrackOptions>,
  ) {
    this.deduplicator = new Deduplicator();
    this.exposure = new ExposureManager(sdk);
    this.dataTrack = new DataTrackBinding(sdk, this.exposure, this.deduplicator);
    this.selectorRule = new SelectorRuleBinding(sdk, this.exposure, this.deduplicator);
    this.attrChange = new AttrChangeBinding(sdk, this.deduplicator);
  }

  async init() {
    // 1. 拉取埋点规则 CDN
    if (this.opts.enableSelectorRules && this.opts.rulesCDNUrl) {
      try {
        const r = await fetch(this.opts.rulesCDNUrl + '?ts=' + Date.now(), { cache: 'default' });
        if (r.ok) this.rules = await r.json();
      } catch (e) { console.warn('[AutoTrack] rules fetch fail', e); }
    }
    this.selectorRule.setRules(this.rules);
  }

  observe(root: Element | Document) {
    // MutationObserver init：监听子节点增删 + data-track 属性 + 规则指定的属性
    const attrFilter = this.buildAttrFilter();
    this.mo = new MutationObserver((records) => this.onMutations(records));
    this.mo.observe(root, {
      childList: true,
      subtree: this.opts.subtree ?? true,
      attributes: true,
      attributeFilter: attrFilter,
      attributeOldValue: true,
      characterData: false,
    });
    // 初始扫描：document 加载完成首次全量绑定
    requestAnimationFrame(() => this.scanRoot(root as Element));
  }

  /** 需要监听哪些属性变化？ */
  private buildAttrFilter(): string[] {
    const set = new Set<string>([
      'data-track-event', 'data-track-on',
      'data-track-props', ...this.datasetAttrWildcards(),
    ]);
    // 配置规则中指定要监听属性变化的属性名也加入
    for (const r of this.rules) if (r.collect.includes('attr')) {
      for (const a of (r.attr_watch ?? [])) set.add(`data-track-${toKebab(a)}`);
    }
    return [...set];
  }
  private datasetAttrWildcards() {
    // data-track-* 所有属性通配：实际 attributeFilter 中只能显式列常见键
    return ['data-track-sku-id','data-track-price','data-track-banner-id','data-track-liked'];
  }

  /** MO 回调 → rAF 批处理 → 扫脏根 → 三通道绑定 */
  private onMutations(records: MutationRecord[]) {
    if (this.stopSignal) return;
    for (const rec of records) {
      switch (rec.type) {
        case 'childList':
          rec.addedNodes.forEach(n => this.dirtyRoots.add(n));
          rec.removedNodes.forEach(n => this.onNodeRemoved(n));
          break;
        case 'attributes':
          this.onAttrChange(rec);
          if (rec.target instanceof Element) this.dirtyRoots.add(rec.target);
          break;
      }
    }
    if (this.rafId == null) this.rafId = requestAnimationFrame(() => this.processDirtyFrame());
  }

  /** 每帧只处理一次：合并所有脏节点，深扫一遍 descendant */
  private processDirtyFrame() {
    this.rafId = null;
    const iter = this.dirtyRoots.values();
    let n = this.dirtyRoots.size;
    const maxPerFrame = this.opts.maxMutationsPerFrame ?? 5000;
    let processed = 0;
    for (const root of iter) {
      if (processed++ > maxPerFrame) break;
      this.scanRoot(root as Element);
    }
    // 超过阈值：下一帧继续（长列表）
    if (n > maxPerFrame && this.dirtyRoots.size) {
      this.rafId = requestAnimationFrame(() => this.processDirtyFrame());
    }
    this.dirtyRoots.clear();
  }

  /** 扫描一个根节点的所有后代，按模式走 data-track / selector-rule / attr 三条绑定链路 */
  scanRoot(root: Element | Node) {
    if (!(root instanceof Element)) return;
    // self first
    this.tryBind(root);
    // descendants
    if (this.opts.subtree ?? true) {
      const walk = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT);
      let el: Node | null = walk.currentNode;
      while ((el = walk.nextNode()) !== null) {
        if (!(el instanceof Element)) continue;
        this.tryBind(el);
      }
    }
  }

  private tryBind(el: Element) {
    if (this.opts.enableDataTrackAttr)   this.dataTrack.tryBind(el);    // 通道一
    if (this.opts.enableSelectorRules)  this.selectorRule.tryBind(el); // 通道二
  }

  private onAttrChange(rec: MutationRecord) {
    if (!(rec.target instanceof Element)) return;
    this.attrChange.dispatch(rec.target, rec.attributeName!, rec.oldValue ?? undefined);
  }

  private onNodeRemoved(node: Node) {
    // 清理：曝光 unobserve + WeakMap 条目清除（WeakMap 本身 GC 自动，但 IO 必须手动 unobserve）
    if (node instanceof Element) this.exposure.unobserveDeep(node);
  }

  disconnect() { this.stopSignal = true; this.mo?.disconnect(); this.exposure.stop(); }
}

function toKebab(name: string) {
  return name.replace(/[A-Z]/g, (m, i) => (i ? '-' : '') + m.toLowerCase());
}
```

### 4.4 data-track 属性点击/曝光自动绑定

```typescript
// sdk/src/auto-track/data-track-binding.ts
import type { TrackingSDK } from '../core/sdk';
import type { TrackingEvent } from '../types';
import { ExposureManager } from './exposure-manager';
import { Deduplicator } from './deduplicator';

export class DataTrackBinding {
  constructor(
    private sdk: TrackingSDK,
    private exposure: ExposureManager,
    private dedup: Deduplicator,
  ) {}

  tryBind(el: Element) {
    // 1. 快速过滤：完全没有 data-track 相关属性的元素跳过
    if (!el.hasAttribute('data-track-event')) return;
    // 2. 去重：同一元素同一通道只绑定一次
    const dedupKey = 'DT:' + (el.getAttribute('data-track-bind-id') ?? genBindId(el));
    if (this.dedup.hit(el, dedupKey)) return;

    const event = el.getAttribute('data-track-event')!;
    const on = (el.getAttribute('data-track-on') ?? 'click|exposure').toLowerCase().split('|') as Array<'click'|'exposure'|'attr'>;
    const props = this.parseProps(el);

    const trackMeta: TrackingEvent['_track'] = {
      source_details: 'data-track',
      data_track_attrs: this.snapshotAttrs(el),
    };

    if (on.includes('click')) {
      el.addEventListener('click', (ev) => {
        this.sdk.track(event, {
          ...props,
          _mouse: { x: (ev as MouseEvent).clientX, y: (ev as MouseEvent).clientY },
        }, { source: 'data-track', _track: trackMeta });
      }, /* capture */ true);
    }
    if (on.includes('exposure')) {
      this.exposure.register(el, {
        event,
        props,
        ratio: Number(el.getAttribute('data-track-exposure-ratio')) || undefined,
        minDuration: Number(el.getAttribute('data-track-exposure-min-duration')) || undefined,
        once: el.getAttribute('data-track-once') !== 'false',
        meta: trackMeta,
      });
    }
    if (on.includes('attr')) {
      // 属性变化的实际绑定交给 AttrChangeBinding（全局统一监听）
      el.setAttribute('data-track-attr-watch', (el.getAttribute('data-track-attr-watch') ?? '*'));
    }
    this.dedup.mark(el, dedupKey);
  }

  /** 同时支持 JSON data-track-props 和 data-track-<key> 分散属性 */
  private parseProps(el: Element): Record<string, any> {
    const out: Record<string, any> = {};
    const jsonStr = el.getAttribute('data-track-props');
    if (jsonStr) {
      try { Object.assign(out, JSON.parse(jsonStr)); } catch (_) { /* invalid json */ }
    }
    for (const attr of el.getAttributeNames()) {
      if (!attr.startsWith('data-track-')) continue;
      if ([
        'data-track-event','data-track-on','data-track-props',
        'data-track-exposure-ratio','data-track-exposure-min-duration',
        'data-track-once','data-track-bind-id','data-track-attr-watch',
      ].includes(attr)) continue;
      const key = attr.slice('data-track-'.length).replace(/-([a-z])/g, (_, g) => g.toUpperCase());
      let v: any = el.getAttribute(attr);
      // 自动转 number/boolean
      if (/^\d+$/.test(v)) v = Number(v);
      else if (v === 'true') v = true;
      else if (v === 'false') v = false;
      out[key] = v;
    }
    return out;
  }

  private snapshotAttrs(el: Element) {
    const out: Record<string, string> = {};
    for (const a of el.getAttributeNames()) if (a.startsWith('data-track-')) out[a] = el.getAttribute(a)!;
    return out;
  }
}

function genBindId(el: Element) {
  const id = 'bid_' + Math.random().toString(36).slice(2, 9);
  el.setAttribute('data-track-bind-id', id);
  return id;
}
```

### 4.5 配置化 CSS Selector 规则埋点（零代码模式）

```typescript
// sdk/src/auto-track/selector-rule-binding.ts
import type { TrackingSDK } from '../core/sdk';
import type { TrackRule } from '../types';
import { ExposureManager } from './exposure-manager';
import { Deduplicator } from './deduplicator';

type Counter = Map<string, { total: number; start: number }>;

export class SelectorRuleBinding {
  private perScopeCounter: Counter = new Map();   // 每个 scope_selector 的命中计数（执行熔断）
  private rules: TrackRule[] = [];

  constructor(
    private sdk: TrackingSDK,
    private exposure: ExposureManager,
    private dedup: Deduplicator,
  ) {}

  setRules(rules: TrackRule[]) { this.rules = rules.filter(r => !this.isBroken(r.rule_id)); }

  tryBind(el: Element) {
    for (const rule of this.rules) {
      if (this.isBroken(rule.rule_id)) continue;
      // 1. 先 scope 过滤
      if (rule.scope_selector && !el.closest(rule.scope_selector)) continue;
      // 2. 主 selector 匹配
      if (!el.matches(rule.element_selector)) continue;
      // 3. 属性过滤
      if (rule.attr_filter && !this.matchAttrFilter(el, rule.attr_filter)) continue;
      // 4. mount_index 过滤
      if (rule.mount_index !== undefined) {
        const seq = this.nextMountSeq(rule);
        if (typeof rule.mount_index === 'number') {
          if (seq !== rule.mount_index) continue;
        } else if (Array.isArray(rule.mount_index)) {
          const [s, e] = rule.mount_index;
          if (seq < s || seq >= e) continue;
        }
      }
      // 5. 执行熔断：单页面 scope 内超过 max 停止
      const fuseKey = rule.scope_selector ? rule.scope_selector + ',' + rule.element_selector : rule.element_selector;
      const counter = this.counterFor(fuseKey);
      counter.total++;
      if (counter.total > (rule.max_matches_per_scope ?? 200)) {
        this.breakRule(rule.rule_id, `scope matches exceed ${counter.total} > 200`);
        continue;
      }

      // 去重 + 绑定
      const dedupKey = 'SEL:' + rule.rule_id;
      if (this.dedup.hit(el, dedupKey)) continue;

      const props = this.collectProps(el, rule);
      const meta: any = { rule_id: rule.rule_id, rule_version: rule.version, selector_matched: rule.element_selector };
      if (rule.collect.includes('mount_index') || typeof rule.mount_index !== 'undefined') {
        props.__mount_seq = counter.total;
      }

      if (rule.collect.includes('click')) {
        const deadline = rule.callback_deadline_ms ?? 3;
        const start = performance.now();
        el.addEventListener('click', () => {
          if (performance.now() - start > deadline) {
            this.breakRule(rule.rule_id, `callback exceeded deadline ${deadline}ms`);
            return;
          }
          this.sdk.track(rule.event, props, { source: 'selector-rule', _track: meta });
        }, true);
      }
      if (rule.collect.includes('exposure')) {
        this.exposure.register(el, {
          event: rule.event,
          props,
          ratio: rule.exposure_ratio ?? 0.5,
          minDuration: rule.exposure_min_duration_ms ?? 1000,
          once: rule.exposure_once ?? true,
          meta,
        });
      }
      this.dedup.mark(el, dedupKey);
    }
  }

  private collectProps(el: Element, rule: TrackRule) {
    const out: Record<string, any> = {};
    for (const [k, spec] of Object.entries(rule.props_map ?? {})) {
      try {
        switch (spec.type) {
          case 'text': {
            const target = spec.selector ? el.querySelector(spec.selector) : el;
            let t = (target?.textContent ?? '').trim();
            if (spec.slice) t = t.slice(spec.slice[0], spec.slice[1]);
            out[k] = t;
            break;
          }
          case 'attr': {
            const target = spec.attr_selector ? el.querySelector(spec.attr_selector) : el;
            out[k] = target?.getAttribute(spec.name) ?? null;
            break;
          }
          case 'dataset': out[k] = (el as HTMLElement).dataset[spec.name] ?? null; break;
          case 'constant': out[k] = spec.value; break;
          case 'mount_seq': out[k] = (spec.start ?? 0) + this.nextMountSeq(rule); break;
        }
      } catch (_) { out[k] = null; }
    }
    return out;
  }

  private counterFor(k: string) {
    if (!this.perScopeCounter.has(k)) this.perScopeCounter.set(k, { total: 0, start: Date.now() });
    return this.perScopeCounter.get(k)!;
  }
  private nextMountSeq(rule: TrackRule) {
    const c = this.counterFor(rule.rule_id);
    return c.total + 1;
  }
  private matchAttrFilter(el: Element, f: Record<string, any>) {
    for (const [k, v] of Object.entries(f)) {
      if (v === null) continue;
      const actual = el.getAttribute(k);
      if (v instanceof RegExp ? !v.test(actual ?? '') : actual !== v) return false;
    }
    return true;
  }
  // 熔断：规则超过执行阈值会被整个页面禁用，不再绑定新元素
  private isBroken(id: string) { return (window as any).__track_broken_rules?.has(id) ?? false; }
  private breakRule(id: string, reason: string) {
    if (!id) return;
    if (!(window as any).__track_broken_rules) (window as any).__track_broken_rules = new Set();
    if ((window as any).__track_broken_rules.has(id)) return;
    (window as any).__track_broken_rules.add(id);
    this.sdk.track('tech_mo_rule_broken', { rule_id: id, reason }, { source: 'auto' });
    console.warn('[AutoTrack] Rule BROKEN:', id, reason);
    this.rules = this.rules.filter(r => r.rule_id !== id);
  }
}
```

### 4.6 MO + IntersectionObserver 联动曝光

```typescript
// sdk/src/auto-track/exposure-manager.ts
import type { TrackingSDK } from '../core/sdk';
import type { TrackingEvent } from '../types';

interface RegOpts {
  event: string;
  props: Record<string, any>;
  ratio?: number;
  minDuration?: number;
  once?: boolean;
  meta?: TrackingEvent['_track'];
}

export class ExposureManager {
  private ioMap: Map<string, IntersectionObserver> = new Map();
  private enterAt = new WeakMap<Element, number>();
  private cfgMap = new WeakMap<Element, RegOpts>();
  private exposed = new WeakSet<Element>();

  constructor(private sdk: TrackingSDK) {}

  register(el: Element, opts: RegOpts) {
    const optsFinal: RegOpts = { ratio: 0.5, minDuration: 1000, once: true, ...opts };
    this.cfgMap.set(el, optsFinal);
    const io = this.getIO(optsFinal.ratio!);
    io.observe(el);
  }

  private getIO(ratio: number): IntersectionObserver {
    const k = ratio.toFixed(2);
    if (!this.ioMap.has(k)) {
      const io = new IntersectionObserver((entries) => {
        for (const e of entries) {
          const el = e.target as Element;
          const cfg = this.cfgMap.get(el)!;
          if (!cfg) continue;
          if (e.isIntersecting && e.intersectionRatio >= (cfg.ratio ?? 0.5)) {
            this.enterAt.set(el, Date.now());
          } else {
            const t0 = this.enterAt.get(el);
            if (t0 && Date.now() - t0 >= (cfg.minDuration ?? 1000)) {
              if (!(cfg.once) || !this.exposed.has(el)) {
                this.exposed.add(el);
                this.sdk.track(cfg.event, {
                  ...cfg.props,
                  _exposure: {
                    duration: Date.now() - t0,
                    ratio: e.intersectionRatio,
                  },
                }, { source: cfg.meta?.rule_id ? 'selector-rule' : 'data-track', _track: cfg.meta });
                if (cfg.once) io.unobserve(el);
              }
            }
            this.enterAt.delete(el);
          }
        }
      }, { threshold: [0, ratio, 1], rootMargin: '0px' });
      this.ioMap.set(k, io);
    }
    return this.ioMap.get(k)!;
  }

  /** 节点被 MO removedNodes 时调用：递归清理，避免内存泄漏 */
  unobserveDeep(root: Element) {
    const walk = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT);
    let n: Node | null = root;
    do {
      if (n instanceof Element) {
        for (const io of this.ioMap.values()) try { io.unobserve(n); } catch(_){}
        this.cfgMap.delete(n);
        this.enterAt.delete(n);
      }
    } while ((n = walk.nextNode()));
  }

  stop() { for (const io of this.ioMap.values()) io.disconnect(); this.ioMap.clear(); }
}
```

### 4.7 去重绑定与性能控制

```typescript
// sdk/src/auto-track/deduplicator.ts
/**
 * 去重逻辑：
 *   同一 Element 同一 "通道"（data-track / selector-rule:rule_id / attr-change）
 *   只能被绑定一次，防止 MO 反复触发同一节点导致重复 addEventListener
 *
 * 为什么不直接用 WeakSet？因为同一元素可能被多条 selector-rule 命中，
 *   所以必须按 "元素 + 维度key" 维度去重。
 */
export class Deduplicator {
  private map = new WeakMap<object, Set<string>>();

  /** 如果已经命中过：返回 true */
  hit(el: Element, key: string): boolean {
    const set = this.map.get(el);
    if (!set) return false;
    return set.has(key);
  }
  mark(el: Element, key: string) {
    let set = this.map.get(el);
    if (!set) { set = new Set(); this.map.set(el, set); }
    set.add(key);
  }
}
```

**性能控制 Checklist（必做，否则 MO 非常容易卡页面）**：

| 控制项 | 默认值 | 说明 |
|-------|-------|------|
| rAF 帧级合并 mutation | ✅ 强制开启 | 一帧最多处理 5000 个脏节点，超过留给下一帧 |
| attributeFilter 白名单 | ✅ 必须 | 不要监听所有属性，只监听 data-track-* 相关和规则指定的 |
| 规则熔断（scope 命中数 + 回调耗时） | 200 元素 / 3ms | 超过立刻 break 该规则，页面内不再生效 |
| subtree 关闭可选项 | 开启 | 已知单页固定 DOM 可关闭 subtree 降低扫描范围 |
| scope_selector 强制限定 | 建议所有规则都填 | `.banner-list .item` 比 `.item` 快 10× |
| IO 共享（按阈值复用） | 按 ratio 分桶 | 相同 ratio 阈值共用一个 IntersectionObserver |
| WeakMap 自动 GC | ✅ | 所有缓存用 WeakMap，组件卸载后浏览器自动回收 |

### 4.8 动态路由与 SPA 组件卸载清理

SPA 应用中 `MO.observe(document)` 是全局的，并不会因为路由切换而自动停止；但**具体 DOM 节点卸载后**，由 Deduplicator 的 WeakMap 和 ExposureManager 的 unobserveDeep 自动清理。路由切换时还需要额外做一件事：重置 `SelectorRuleBinding.perScopeCounter` 计数，否则第 2 页一开始就会因 scope 命中数超 200 被熔断。

```typescript
// sdk/src/integrations/router-plugin.ts (MO 版本增强)
import type { Router } from 'vue-router';
import type { TrackingSDK } from '../core/sdk';
import { AutoTrackEngine } from '../auto-track/engine';

export function bindVueRouter(sdk: TrackingSDK, router: Router, autoTrack?: AutoTrackEngine) {
  router.afterEach(() => {
    // 路由切换 → 重置 per-scope 命中计数（防止熔断）
    if (autoTrack) {
      autoTrack['selectorRule']['perScopeCounter'].clear();
      (window as any).__track_broken_rules?.clear();
    }
    sdk.track('page_view', {}, { source: 'auto' });
  });
}
```

---

## 五、埋点配置化管理平台

### 5.1 规则管理平台架构

```
埋点平台（前端 + 后端）
├── 规则列表页：按业务线/事件名/owner 搜索 → 查看命中量/报错率
├── 规则编辑页
│   ├── 左：页面 iframe 预览 + Chrome 扩展点选元素 → 自动生成稳定 selector
│   ├── 右：表单配置 event、collect(click/exposure/attr)、props_map、scope_selector
│   └── 调试区：DevTools 显示 "该规则当前页面命中 12 个元素，采样 props 如下"
├── 版本与审批：新建规则版本 → PM+FE+QA 三方审批 → 灰度 → 全量
└── 监控页：每条规则命中事件量、熔断次数、回调 p99 耗时 → 超阈值告警 owner
```

### 5.2 规则动态下发与灰度发布

```typescript
// 服务端：规则 CDN 生成（Node 定时 + 上传 OSS）
// 灰度策略：按 distinct_id.hash % 100 < 灰度比例
import murmurhash from 'murmurhash';

export async function publishRules(rules: TrackRule[], grayPct: number) {
  const meta = { version: 'v_' + Date.now(), gray_pct: grayPct, update_at: new Date().toISOString() };
  const payload = JSON.stringify({ meta, rules }, null, 2);
  await OSS.put('/track-rules/latest.json', payload);
  await OSS.put(`/track-rules/${meta.version}.json`, payload); // 归档版本可回滚
}

// SDK 端：灰度判断
export function hitGray(distinctId: string, pct: number) {
  const hash = murmurhash.v3(distinctId) >>> 0;
  return (hash % 100) < pct;
}
```

### 5.3 可视化规则生成（Chrome 插件点选）

Chrome 扩展 content-script，注入 `document_start`，监听 alt+点击元素时弹出生成器：

```js
// chrome-extension/content.js
document.addEventListener('click', (e) => {
  if (!e.altKey) return;
  e.preventDefault();
  e.stopPropagation();
  const el = e.target;
  const selector = buildStableSelector(el);
  const text = (el.textContent || '').trim().slice(0, 50);
  chrome.runtime.sendMessage({
    action: 'track_rule_generate',
    payload: {
      element_selector: selector,
      preview_text: text,
      preview_props: extractDatasetProps(el), // data-track 或自动 dataset
    }
  });
}, true);

/** 稳定 Selector 生成：优先级 id > data-* > nth-child，尽量避免动态 class */
function buildStableSelector(el) {
  if (el.id) return `#${CSS.escape(el.id)}`;
  const dataId = [...el.getAttributeNames()].find(a => a.startsWith('data-track-id'));
  if (dataId) return `[${dataId}="${CSS.escape(el.getAttribute(dataId)!)}"]`;
  // 父级回溯直到遇到唯一组合
  const parts = [];
  let cur = el;
  for (let depth = 0; depth < 6 && cur !== document.body; depth++, cur = cur.parentElement!) {
    const tag = cur.tagName.toLowerCase();
    const same = Array.from(cur.parentElement!.children).filter(c => c.tagName === cur.tagName).length;
    const idx = Array.from(cur.parentElement!.children).indexOf(cur) + 1;
    parts.unshift(same > 1 ? `${tag}:nth-of-type(${idx})` : tag);
    const candidate = parts.join(' > ');
    if (document.querySelectorAll(candidate).length === 1) return candidate;
  }
  return parts.join(' > ');
}
```

---

## 六、服务端处理与存储

### 6.1 Fastify 网关：限流、补维、写入 Kafka

```typescript
// server/src/app.ts
import fastify from 'fastify';
import { Type } from '@fastify/type-provider-typebox';
import { Kafka } from 'kafkajs';
import { BloomFilter } from 'bloom-filters';
import { parseUA } from './ua';
import { parseGeo } from './geo';
import { cleanEvent, desensitize } from './clean';

const app = fastify({ trustProxy: true });
const kafka = new Kafka({ brokers: ['k1:9092','k2:9092','k3:9092'] });
const producer = kafka.producer();
producer.connect();
const bloom = BloomFilter.create(50_000_000, 0.001); // 50M 容量,误判 0.1%

const BatchSchema = Type.Object({
  app_id: Type.String(), events: Type.Array(Type.Any())
});

app.post('/v1/events', { schema: { body: BatchSchema } }, async (req, reply) => {
  const body = req.body as any;
  const ip = (req.headers['x-forwarded-for'] as string)?.split(',')[0] ?? req.ip;
  const ua = req.headers['user-agent'] ?? '';
  const uai = parseUA(ua); const geo = parseGeo(ip);
  const out: any[] = [];
  for (const e of body.events) {
    if (!bloom.addIfAbsent(e.event_id)) continue; // 去重
    const cleaned = cleanEvent(e, { ua: uai, geo, ip, app_id: body.app_id });
    if (!cleaned) continue;
    cleaned.properties = desensitize(cleaned.properties);
    out.push(cleaned);
  }
  if (!out.length) return reply.code(204).send();
  await producer.send({
    topic: 'tracking_events',
    messages: out.map(e => ({
      key: e.distinct_id, value: JSON.stringify(e),
    })),
  });
  return { ok: true, n: out.length };
});

app.listen({ port: 3000, host: '0.0.0.0' });
```

### 6.2 数据清洗与脱敏

```typescript
// server/src/clean.ts
export function cleanEvent(raw: any, extra: any): any | null {
  const required = ['event', 'event_id', 'timestamp', 'distinct_id'];
  if (!required.every(k => typeof raw[k] === 'string' && raw[k].length)) return null;
  if (raw.event.length > 48 || !/^[a-z][a-z0-9_]{1,47}$/.test(raw.event)) return null;
  const drift = Math.abs(Date.now() - raw.timestamp);
  if (drift > 24 * 3600_000) raw.timestamp = Date.now();
  const properties = typeof raw.properties === 'object' ? raw.properties : {};
  const propLen = Buffer.byteLength(JSON.stringify(properties), 'utf8');
  if (propLen > 8_192) return { ...raw, properties: { _truncated: true }, ...extra };
  return { ...raw, properties, partition_date: new Date(raw.timestamp).toISOString().slice(0, 10), ...extra };
}

export function desensitize(props: Record<string, any>) {
  const out: any = {};
  for (const [k, v] of Object.entries(props)) {
    if (typeof v !== 'string') { out[k] = v; continue; }
    if (/mobile|phone|^tel$/i.test(k)) out[k] = v.replace(/^(\d{3})\d{4}(\d{4})$/, '$1****$2');
    else if (/email/i.test(k)) out[k] = v.replace(/^(.).*(@.)/, '$1***$2');
    else if (/id_card|idcard|身份证/i.test(k)) out[k] = v.replace(/^(.{6}).*(.{4})$/, '$1********$2');
    else out[k] = v;
  }
  return out;
}
```

### 6.3 ClickHouse 建表语句

```sql
CREATE DATABASE IF NOT EXISTS tracking;

CREATE TABLE tracking.events_kafka
(
    event String, event_id String, timestamp Int64,
    source LowCardinality(String),
    user_id Nullable(String), anonymous_id String, distinct_id String,
    login_status LowCardinality(String),
    platform LowCardinality(String), os String, browser String,
    screen_resolution String, network_type String,
    page_path String, page_referrer String, ab_test_group Nullable(String),
    session_id String, session_event_index Int32,
    geo_country FixedString(2), geo_province String, geo_city String,
    properties String,
    _track String
)
ENGINE = Kafka
SETTINGS
    kafka_broker_list = 'k1:9092,k2:9092,k3:9092',
    kafka_topic_list   = 'tracking_events',
    kafka_group_name   = 'clickhouse_consumer',
    kafka_format       = 'JSONEachRow',
    kafka_num_consumers = 4;

CREATE TABLE tracking.events
(
    partition_date Date,
    event String,
    event_id String,
    timestamp DateTime64(3),
    source LowCardinality(String),
    distinct_id String,
    geo_country FixedString(2),
    geo_province String,
    geo_city String,
    page_path String,
    session_id String,
    properties String,
    _track String
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(partition_date)
ORDER BY (event, partition_date, cityHash64(distinct_id))
TTL partition_date + INTERVAL 365 DAY DELETE
SETTINGS index_granularity = 8192;

CREATE MATERIALIZED VIEW tracking.events_mv TO tracking.events AS
SELECT
    toDate(timestamp / 1000)         AS partition_date,
    event, event_id,
    fromUnixTimestamp64Milli(timestamp) AS timestamp,
    source, distinct_id,
    geo_country, geo_province, geo_city,
    page_path, session_id, properties, _track
FROM tracking.events_kafka;

-- 日聚合视图
CREATE MATERIALIZED VIEW tracking.daily_pvuv
ENGINE = SummingMergeTree PARTITION BY toYYYYMM(dt) ORDER BY (dt, event, source)
AS
SELECT
    partition_date          AS dt,
    event,
    source,
    count()                 AS pv,
    uniqExact(distinct_id)  AS uv,
    uniqExact(session_id)   AS sessions
FROM tracking.events
GROUP BY dt, event, source;
```

---

## 七、看板、告警、性能与合规

### 7.1 三类 Grafana 看板设计

| 看板名 | 核心指标 | ClickHouse 查询模式 |
|-------|---------|-------------------|
| **业务看板** | DAU、PV、点击率、GMV、漏斗 | 从 daily_pvuv 聚合视图；漏斗用 multiIf + anyLast 窗口 |
| **MO 自动化看板** | 规则命中数、熔断次数、data-track 采量占比、scope p99 扫描耗时 | `SELECT count() WHERE source IN ('data-track', 'selector-rule') GROUP BY event, source` |
| **性能与异常看板** | LCP/INP/CLS 分位数、JS 错误率、MO 回调 p95 耗时 | 事件名 `tech_web_vitals`、`tech_js_error`、`tech_mo_rule_broken` |

### 7.2 Prometheus 四级告警规则

```yaml
groups:
  - name: tracking
    rules:
      - alert: P0_TrackPVPlunge
        expr: rate(track_pv[1h]) / rate(track_pv[1h] offset 1d) < 0.5
        for: 15m
        labels: { severity: P0 }
        annotations: { summary: "PV 较昨日下跌 > 50%" }

      - alert: P1_MORuleBroken
        expr: increase(track_mo_rule_broken_total[1h]) > 3
        for: 5m
        labels: { severity: P1 }
        annotations: { summary: "MO 规则 1 小时内熔断超过 3 次" }

      - alert: P1_JsErrorRate
        expr: sum(rate(track_event_count{event="tech_js_error"}[1h])) / sum(rate(track_event_count{event="page_view"}[1h])) > 0.02
        for: 1h
        labels: { severity: P2 }

      - alert: P2_LCPPoor
        expr: quantile(0.5) (track_lcp{rating="poor"}) without(instance) > 4000
        for: 2h
        labels: { severity: P2 }
```

### 7.3 MO 对主线程的占用控制

**预算：每日活跃页面 10 秒窗口内，MO 相关回调耗时 ≤ 50ms（占用 ≤ 0.5%）。**

压测验证：在 `mutation 1000次/s` 的页面（如虚拟滚动表格），打开 MO + 20 条配置规则，用 Chrome Performance 录制 60s，统计 Long Task 数量不应超过 3 条（单条 > 50ms）。若超过则排查：

1. 是否配置了过宽的选择器（如 `.el-button` → 页面 5000 个按钮全扫）
2. 是否 `props_map` 中使用了过深的 DOM 查询（`.querySelectorAll('.foo .bar')` 千级节点）
3. 是否开启了不必要的 subtree 监听（可限定 scope_selector 到局部容器）

### 7.4 隐私合规（个保法/GDPR）

1. **未授权不上报**：MO 引擎初始化延迟到 CMP 弹窗确认后；未授权阶段 `observe()` 不调用
2. **数据最小化**：`_track.selector_matched`、`dom_path` 在 SDK 端默认不采集，仅当规则 owner 手动声明 debug=true 时开启，7 天自动过期
3. **敏感词属性剔除**：服务端 properties 除了正则打码，还额外扫 DOM 属性文本，自动剔除匹配手机号/身份证正则的字段值
4. **被遗忘权**：`POST /api/v1/privacy/forget { distinct_id }` → MySQL 登记 → 每小时 ClickHouse mutation 执行 `ALTER DELETE WHERE distinct_id IN (xxx)`，按每月分区分批执行防 IO 打爆

---

## 八、实施落地与面试题集


### 8.2 MO 埋点常见问题排查手册

| 现象 | 根因 Top3 | 排查步骤 |
|-----|----------|---------|
| **MO 采到的数据比手动埋点少** | ① scope_selector 范围写小了漏匹配 ② `attributeFilter` 未包含 data-track-event 导致属性变更时未触发 ③ `subtree:false` 但组件实际嵌套了子树 | ① 在 Console 跑 `document.querySelectorAll(selector)` 核对命中数 ② DevTools Sources → Mutation Breakpoints 看是否触发回调 ③ MO 初始化参数打印确认 |
| **MO 同一个按钮点一下报 2 次** | ① 同一元素既带 data-track 属性，又命中了配置规则 selector，两条通道各绑一次 ② 热更新/MO 回调重复绑定，去重 key 错误 | ① 控制台 `console.log(el)` → 展开 WeakMap dedup 条目，查看命中了几个 key ② SDK debug=true 模式会打印 `[dedup] HIT` vs `[dedup] MISS` 日志 |
| **配置规则下发后不生效** | ① 灰度比例 0% 未命中 ② 规则发布到 CDN 但未刷新 ETag，浏览器缓存旧版本 ③ 规则已被熔断（性能阈值超了） | ① `localStorage.track_force_gray=1` 强制命中 100% 再看 ② Network 面板检查 rules.json 响应头 ETag/Last-Modified ③ `(window as any).__track_broken_rules` 查看熔断的 rule_id |
| **曝光不触发** | ① 容器是 overflow:auto 的滚动盒子，但 IO.root 是默认 viewport ② 曝光阈值 ratio 设太高（0.9）但卡片只有一半显示 ③ 节点 mounted 后立马被父组件 CSS 动画 translate 移出视口 | ① 指定 IO root 参数为滚动容器（本方案 SDK 默认 viewport，需在规则里声明滚动父 scope） ② 用 Chrome DevTools Layers 面板观察元素真实位置 ③ 增加 minDuration 容忍动画周期 |
| **页面卡 Long Task > 100ms** | ① 配置了 200 条规则同时生效 ② 某条规则的 props_map.text.slice 调用了大段 innerText 解析 ③ scope_selector 空 → 每次 mutation 全 document 扫 | ① `performance.mark` 在 tryBind 开始/结束打点，分规则累计耗时 Top10 ② scope_selector 强制必填，拒绝空值 ③ 执行熔断自动 break 并告警 owner |

### 8.3 前端埋点监控面试题（MutationObserver 专题）

**Q1：MutationObserver 和 IntersectionObserver 分别在埋点里适合什么场景？为什么不能只用一个？**

> **答案**：MutationObserver 监听 DOM 结构和属性变化，擅长"发现新元素并自动绑定"；IntersectionObserver 监听元素是否进入视口，擅长"判断曝光是否达标"。两者不能互替：MO 只能知道元素挂载了，但不知道它何时真正被用户看到；IO 只能观察注册过的元素，不知道异步渲染何时把新元素插入 DOM。正确联动是 MO callback 里把新节点交给 IO.observe，各取所长。
>
> **知识点**：MO/IO 双监听器分工
> **难度**：初级

**Q2：为什么 MO 回调里要做 requestAnimationFrame 批处理？直接在回调里扫所有新增节点不行吗？**

> **答案**：因为 MO 回调触发非常高频——一次 React 组件渲染可能产生几十到几百条 childList/attributes mutation record，如果每条都深度扫描，一帧内会累计上百次重复扫描同一子树，造成主线程长任务。用 rAF 把同一帧内所有 mutation 合并成一次 scan，相当于"帧级防抖"。并且可以对单次扫描的元素数量上限做阈值，超过的部分留给下一帧，保证用户交互不会被卡。
>
> **知识点**：rAF 合并、长任务治理
> **难度**：中级

**Q3：MO 自动绑定的去重策略是什么？同一元素被 data-track 和配置规则同时命中怎么办？**

> **答案**：去重按 "Element + 通道 key" 双维度用 WeakMap + Set 做。通道 key 示例：data-track 通道是 `DT:<bind-id>`，每条配置规则是 `SEL:<rule_id>`，属性变化通道是 `ATTR:<attr>`。这样同一元素可以被多条规则命中（如一个 Banner 同时被 "首页Banner曝光" 和 "运营活动曝光" 两条规则采集），但同一通道同一元素只会被绑定一次，避免重复 addEventListener。双命中时正常上报两条，因为语义不同（业务方就是希望从两个视角统计同一元素）。
>
> **知识点**：多通道去重设计
> **难度**：中级

**Q4：线上 MO 自动化埋点导致页面卡顿，设计一套性能监控 + 熔断 + 自愈方案。**

> **答案**：分四层：
>
> 1. **规则级熔断**：单 scope 内某规则命中超过 200 个元素、或单元素 props_map 采集回调超过 deadline（默认 3ms），立刻将该 rule_id 加入 `__track_broken_rules`，页面生命周期内不再生效，并上报 `tech_mo_rule_broken` 事件告警 owner。
> 2. **帧级节流**：每帧最多扫 5000 个脏节点，超过留给下一帧；同时监控 MO 累计耗时占比，连续 3 帧 > 50ms 自动切 `performance-mode = performance-first`（关闭 subtree 遍历、只扫 scope_selector）。
> 3. **监控告警**：Grafana 按 1 分钟粒度展示"MO 回调 p95/p99 耗时"、"规则熔断次数"、"自动埋点事件量占比"三项关键指标，超过阈值 P1 告警。
> 4. **自愈**：规则平台每次发布新版本，CDN JSON 版本号变更 → SDK 定时 3 分钟拉一次 rules，命中新版本后清空熔断集合、重置计数器，并验证新版 p95 耗时是否回落；若规则发布 10 分钟内仍被熔断则自动回滚上一版。
>
> **知识点**：熔断设计、自愈、性能预算
> **难度**：高级

---

## 参考资料

- [DOM Standard - MutationObserver（W3C 官方）](https://dom.spec.whatwg.org/#mutation-observers)
- [DOM Standard - IntersectionObserver](https://www.w3.org/TR/intersection-observer/)
- [navigator.sendBeacon - W3C Beacon](https://w3c.github.io/beacon/)
- [ClickHouse MergeTree + TTL + Kafka 引擎（官方文档）](https://clickhouse.com/docs/zh/engines/table-engines/mergetree-family/)
- [Kafka 3.x JavaScrit Client（kafkajs）](https://kafka.js.org/)
- [MutationObserver 性能最佳实践（Google Web Fundamentals）](https://developer.chrome.com/blog/detect-dom-changes-with-mutation-observers/)
- [《信息安全技术 个人信息安全规范》GB/T 35273-2020](https://openstd.samr.gov.cn/)
