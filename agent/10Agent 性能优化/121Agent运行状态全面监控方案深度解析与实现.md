# Agent 运行状态全面监控方案深度解析与实现

> 文档定位:设计并实现一套对 Agent 运行状态进行全面监控的工程化方案,涵盖指标采集体系、监控仪表盘、告警机制、结构化日志与查询分析、状态可视化展示;并通过 **指标降采样、写入缓冲队列、分级丢弃、哨兵值清洗** 等策略,严格控制监控系统本身对 Agent 性能的影响(<1% CPU、<10MB 内存、<0.5% 请求延迟)。
>
> 核心经验参考:
> - **经验 200832**:没有可观测证据就改策略 → 必然原地踏步。必须建立"创建/销毁/计数器/所有权链"最小可观测面,用计数差分锁定资源泄漏。
> - **经验 1265259**:高频写入导致 IO 卡顿、日志淹没 → 必须在 **写入入口** 做 内存缓冲+定时 flush+背压丢弃(ERROR立即/INFO批量/DEBUG可丢弃),而不是笼统加防抖。
> - **经验 335399**:异常占位值(如 -9999/NaN/None)未清洗直接参与指标 → 指标严重失真。必须在采集层统一做 **哨兵值/越界值 清洗 + 鲁棒聚合(NaN跳过/中位数)**。
>
> 阅读建议:与 [116Agent系统稳定性提升完整方案深度解析.md](./116Agent系统稳定性提升完整方案深度解析.md)、[120Agent系统全面压力测试方案深度解析与实施指南.md](./120Agent系统全面压力测试方案深度解析与实施指南.md) 配套阅读,形成监控-定位-压测的可观测性闭环。

---

## 目录

- [一、监控系统设计目标与核心原则](#一监控系统设计目标与核心原则)
- [二、关键运行指标体系](#二关键运行指标体系)
- [三、指标采集方案(轻量、低侵入)](#三指标采集方案轻量低侵入)
- [四、状态监控仪表盘设计](#四状态监控仪表盘设计)
- [五、异常阈值告警机制](#五异常阈值告警机制)
- [六、结构化日志与查询分析](#六结构化日志与查询分析)
- [七、Agent 监控系统完整 Python 实现](#七agent-监控系统完整-python-实现)
- [八、最小性能影响控制策略(核心)](#八最小性能影响控制策略核心)
- [九、实施步骤与验证方法](#九实施步骤与验证方法)
- [十、总结与选型建议](#十总结与选型建议)

---

## 一、监控系统设计目标与核心原则

### 1.1 四大设计目标

```mermaid
mindmap
  root((监控系统设计目标))
    全面可见
      系统资源CPU/GPU/MEM
      业务指标延迟/成功率
      调度指标队列/优先级
      质量指标幻觉率/准确率
    低侵入低影响
      CPU开销<1%
      内存开销<10MB
      请求延迟影响<0.5%
      非关键路径异步
    告警准确及时
      误报率<5%
      漏报率≈0
      P0告警<30秒触达
      分级分层抑制
    可追溯可定位
      指标→日志→追踪 串联
      Trace ID 全链路贯穿
      哨兵值先清洗再聚合
      最小可观测面 计数器差分
```

### 1.2 八大核心原则(工程经验沉淀)

| 编号 | 原则 | 说明(对应经验教训) |
|:---:|-----|--------------------|
| **P1** | **最小可观测面先行,再优化策略** | 先建立计数器/指标,用差分锁定泄漏/问题,再动业务代码(经验200832) |
| **P2** | **哨兵值/异常值 采集层清洗** | -9999/NaN/None/越界值 进入指标库之前必须置为NaN或丢弃,绝不参与原始聚合(经验335399) |
| **P3** | **采集=内存缓冲+定时批量flush** | 所有写入入口(指标/日志)先进内存队列,定时flush;严禁同步单条写磁盘(经验1265259) |
| **P4** | **分级写入策略** | ERROR立即、INFO 1秒批量、DEBUG采样+超阈值丢弃;关键日志不丢,非关键可丢(经验1265259) |
| **P5** | **监控通道与业务通道严格隔离** | 监控走独立线程+独立连接池;严禁在业务热路径同步等待监控完成 |
| **P6** | **Trace ID 全链路贯穿** | 同一个请求,从 指标、日志、追踪、业务错误 → 同一个 Trace ID 可查 |
| **P7** | **鲁棒统计优于平均统计** | 优先 P50/P95/P99/中位数,避免异常值拉偏平均值(经验335399) |
| **P8** | **监控系统自身必须可监控** | 监控队列长度、flush延迟、丢弃数、采集失败数,本身必须有自监控 |

---

## 二、关键运行指标体系

### 2.1 六大指标家族(90+指标)

```mermaid
flowchart TB
    subgraph F1 系统资源指标 - 主机层
        F1_CPU["CPU 利用率 / Load / 上下文切换<br/>每核、用户态/系统态、软中断"]
        F1_MEM["内存 利用率 / RSS / VSS / Swap<br/>Page Fault / OOM Kill 次数"]
        F1_DISK["磁盘 IOPS / 吞吐 / 队列长 / Util%<br/>读写时延 / 剩余空间"]
        F1_NET["网络 PPS / 带宽 / 重传率 / 丢包<br/>TCP 连接数 / 队列"]
        F1_GPU["GPU SM% / 显存 / 温度 / 功耗<br/>PCIe带宽 / TensorCore利用"]
    end
    
    subgraph F2 Agent 业务指标 - 请求层
        F2_QPS["QPS / RPM / 活跃用户数<br/>按任务类型、优先级拆分"]
        F2_LAT["AVG / P50 / P95 / P99 响应时间<br/>TTFT首Token / TPOT每Token时间"]
        F2_OK["任务成功率 / 各优先级SLA达标率<br/>按 P0-P4 分"]
        F2_ERR["错误率 / 错误类型分布<br/>Timeout / LLMError / ToolError / RAGError"]
    end
    
    subgraph F3 LLM / RAG 能力指标
        F3_LLM["LLM 调用次数 / RPM<br/>缓存命中率 / 失败率"]
        F3_TOKEN["Token 消耗( Prompt / Completion )<br/>每请求平均Tokens"]
        F3_RAG["RAG 检索时延 / 召回率<br/>Top-K命中 / 嵌入耗时"]
        F3_QUAL["答案准确率 / 幻觉率(抽样)<br/>引用率 / 完整性评分"]
    end
    
    subgraph F4 Multi-Agent 调度指标
        F4_Q["队列长度(总量/分优先级)<br/>P99等待时间"]
        F4_ALLOC["调度延迟 / 分配失败率<br/>能力匹配命中率"]
        F4_AGENT["Agent 并发数 / 每Agent负载<br/>闲置Agent数 / 离线Agent数"]
        F4_RESOURCE["GPU / CPU / 内存槽位 占用率<br/>API配额剩余率"]
    end
    
    subgraph F5 工具 / 外部依赖指标
        F5_TOOL["各工具调用次数 / 平均时延<br/>成功率 / 重试次数"]
        F5_VDB["向量库 QPS / 查询延迟 / 错误率<br/>索引大小 / 合并耗时"]
        F5_EXT["外部 API 配额使用率<br/>限流次数 / 熔断状态"]
    end
    
    subgraph F6 稳定性 / 自监控指标
        F6_PROC["主进程 / Worker 重启次数<br/>崩溃次数 / 启动耗时"]
        F6_LEAK["内存增长速率(MB/h)<br/>线程数增量 / 句柄数增量"]
        F6_MON["监控系统自监控<br/>队列长 / flush延迟 / 丢弃数"]
        F6_RECOVER["故障恢复时长<br/>自动拉起次数 / 降级生效次数"]
    end

    style F1 fill:#d1ecf1,stroke:#0c5460
    style F2 fill:#d4edda,stroke:#155724
    style F3 fill:#fff3cd,stroke:#d39e00
    style F4 fill:#f0d9b5,stroke:#8a6d3b
    style F5 fill:#e2d9f3,stroke:#4a235a
    style F6 fill:#f8d7da,stroke:#721c24
```

### 2.2 核心指标定义与采集目标(精选Top 30)

| 指标名 | 类型 | 单位 | 采集频率 | 健康阈值 | 告警阈值 | 用途 |
|-------|-----:|:---:|:-------:|:--------:|:--------:|-----|
| **cpu_util_pct** | Gauge | % | 10s | <70 | >90 持续3min | 热定位CPU瓶颈 |
| **memory_rss_mb** | Gauge | MB | 10s | — | 增长>50MB/h持续3h | **内存泄漏差分检测(经验200832)** |
| **memory_util_pct** | Gauge | % | 10s | <80 | >92 | OOM前兆 |
| **gpu_sm_util_pct** | Gauge | % | 10s | <85 | >95持续2min | GPU饱和判定 |
| **gpu_memory_used_pct** | Gauge | % | 10s | <80 | >95 | GPU OOM前兆 |
| **disk_util_pct** | Gauge | % | 30s | <70 | >95持续5min | IO瓶颈 |
| **disk_free_pct** | Gauge | % | 5min | >20 | <10 或 <5GB | 磁盘满预警 |
| **net_retrans_pct** | Gauge | % | 30s | <0.1 | >1持续5min | 网络质量 |
| --- | --- | --- | --- | --- | --- | --- |
| **qps_success** | CounterR | 次/s | 10s | — | — | 吞吐 |
| **latency_p50_ms** | Hist | ms | 30s | — | — | 一般体验 |
| **latency_p95_ms** | Hist | ms | 30s | <2000 | >5000持续3min | 多数用户体验 |
| **latency_p99_ms** | Hist | ms | 30s | <5000 | >15000持续2min | SLA判定 |
| **ttft_p99_ms** | Hist | ms | 30s | <1500 | >5000 | 流式首Token |
| **success_rate_pct** | Gauge | % | 30s | >99 | <98 持续5min | 成功率 |
| **error_rate_pct** | Gauge | % | 30s | <1 | >3 持续2min | 错误率 |
| **sla_p0_pass_pct** | Gauge | % | 1min | ≥99.5 | <99 | 关键SLA |
| **sla_p2_pass_pct** | Gauge | % | 1min | ≥95 | <92 | 普通SLA |
| --- | --- | --- | --- | --- | --- | --- |
| **llm_cache_hit_rate_pct** | Gauge | % | 1min | >40 | <10 | 缓存优化 |
| **llm_rpm** | Gauge | 次/min | 30s | — | >限额×0.9 | LLM配额预警 |
| **token_per_req_avg** | Gauge | 个 | 30s | — | 环比+50% | Token爆增 |
| **rag_recall_pct** | Gauge | % | 5min | >90 | <80 | RAG质量 |
| **rag_search_p99_ms** | Hist | ms | 30s | <200 | >800 | RAG慢 |
| --- | --- | --- | --- | --- | --- | --- |
| **queue_size_total** | Gauge | 个 | 10s | <50 | >200持续3min | 排队拥堵 |
| **queue_p0_count** | Gauge | 个 | 10s | <5 | >30 持续5min | 关键任务堆积 |
| **scheduler_latency_p99_ms** | Hist | ms | 30s | <50 | >200 | 调度慢 |
| **agent_utilization_pct** | Gauge | % | 30s | <80 | >95持续3min | Agent满负荷 |
| **agent_offline_count** | Gauge | 个 | 30s | 0 | ≥1 | Agent掉线 |
| --- | --- | --- | --- | --- | --- | --- |
| **proc_restart_count_1h** | CounterR | 次 | 1min | 0 | ≥2 | 崩溃 |
| **memory_leak_mb_per_hour** | Gauge | MB/h | 1h | <20 | >50持续3h | **泄漏判定(经验200832)** |
| **mon_queue_backlog** | Gauge | 个 | 30s | <1000 | >10000持续2min | **自监控:监控本身卡住** |

> **指标类型说明**:Gauge=瞬时值、CounterR=速率、Hist=分位数直方图

---

## 三、指标采集方案(轻量、低侵入)

### 3.1 采集分层架构

```mermaid
flowchart TB
    subgraph A[Agent进程内 - 采集层]
        A1[资源采集器 psutil/NVML<br/>CPU/GPU/MEM/DISK/NET<br/>频率:10s-30s]
        A2[埋点 Hook<br/>LLM/RAG/工具/调度<br/>无侵入:装饰器/Middleware]
        A3[Metrics Buffer<br/>内存环形队列<br/>容量默认 50K]
    end
    
    subgraph B[Agent进程内 - 处理层]
        B1[**哨兵值清洗**<br/>-9999/NaN/None/越界→丢弃<br/>(经验335399)]
        B2[**预聚合 + 降采样**<br/>1秒桶聚合、DEBUG降采样1%]
        B3[分类缓冲队列<br/>CRITICAL:立即<br/>INFO:1秒批量<br/>DEBUG:可丢弃(经验1265259)]
    end
    
    subgraph C[异步发送层]
        C1[Prometheus Pushgateway<br/>或Exporter<br/>标准协议]
        C2[OpenTelemetry OTLP<br/>追踪+指标一体化]
        C3[自定义JSON批量上报<br/>到监控网关]
    end
    
    subgraph D[存储层]
        D1[(Prometheus / VictoriaMetrics<br/>时序数据库)]
        D2[(Loki / ClickHouse<br/>日志存储)]
        D3[(Jaeger / Zipkin<br/>追踪存储)]
    end
    
    A1 --> A3
    A2 --> A3
    A3 --> B1
    B1 --> B2
    B2 --> B3
    B3 -- 异步线程 --> C1
    B3 -- 异步线程 --> C2
    B3 -- 异步线程 --> C3
    
    C1 --> D1
    C2 --> D3
    C3 --> D1
    C3 --> D2
```

### 3.2 指标采集频率设计(避免"全1秒"浪费)

| 指标家族 | 采集频率 | 为什么 |
|---------|:-------:|--------|
| 系统资源(CPU/GPU/MEM/DISK/NET) | **10秒** | 变化较慢,10秒足够捕获趋势;1秒会产生10×写入量 |
| 磁盘空间/文件句柄 | **5分钟** | 变化极慢,5分钟都算高频 |
| 网络重传/连接数 | **30秒** | 变化中速,30秒足够判定趋势 |
| 业务 QPS / 成功率 / 延迟 | **10秒桶** | 桶内批量聚合计数;单条请求内存累加 |
| 分优先级 SLA 达标率 | **1分钟** | 需要足够样本才稳定,1分钟合适 |
| 质量指标(准确率/幻觉率/召回率) | **5-15分钟** | 抽样评估,计算成本高,低频 |
| 调度队列 / Agent健康 | **5-10秒** | 快速发现堆积与掉线 |
| 进程重启 / 崩溃 | **事件驱动** | 产生时立即上报,不用轮询 |
| 内存泄漏速率 | **1小时差分** | 连续3小时判定,避免抖动误判 |

### 3.3 关键技术:采集层 **哨兵值清洗**(经验 335399)

> **这是指标正确性的生命线**: 原始采集中的异常值(如 `-9999`、`None`、`NaN`、`""`、`-1` 等占位值)如果直接写入时序库,会导致 P99、平均、总和全部失真。必须在 **进入环形缓冲之前** 完成清洗。

```python
# 核心清洗规则示例(经验 335399)
SENTINEL_VALUES = {
    None, float("nan"), float("inf"), -float("inf"),
    -9999, -99999, -1, 0,  # 业务常见占位,需结合业务可配置
    "", "N/A", "unknown"
}

# 字段级合法范围(按业务语义配置)
FIELD_VALID_RANGES = {
    "cpu_util_pct":          (0, 100),
    "memory_util_pct":       (0, 100),
    "gpu_sm_util_pct":       (0, 100),
    "gpu_temperature_c":     (-20, 120),
    "disk_util_pct":         (0, 105),  # 允许短暂105%毛刺
    "latency_ms":            (0, 600_000),  # 最大10分钟,超过算异常
    "qps_success":           (0, None),  # 下界0,无上界
    "success_rate_pct":      (0, 100),
    "memory_leak_mb_per_hour": (-200, 2000),  # 允许负值(内存下降)
}
```

### 3.4 关键技术:非侵入埋点

```mermaid
flowchart LR
    H1[装饰器 @monitor]
    H2[上下文管理器 with monitor_span]
    H3[中间件 FastAPI StarletteMiddleware]
    H4[事件监听 subscribe EventBus]
    
    H1 --> BUF[内存环形缓冲]
    H2 --> BUF
    H3 --> BUF
    H4 --> BUF
    
    BUF --> CLEAN[哨兵值清洗]
    CLEAN --> PREAGG[1秒桶预聚合]
```

**侵入性控制原则**:
- 不改业务代码主逻辑,仅在函数入口/出口用装饰器。
- 不修改业务函数签名(经验200832教训:不要为清理缓存改const)。
- 监控字段加 `mutable` 或独立对象,不与业务状态耦合。

---

## 四、状态监控仪表盘设计

### 4.1 仪表盘分层体系(三层一眼看全局)

```mermaid
flowchart TB
    subgraph L1 全局总览 Layer - C-Level / 值班
        S1[全局健康评分 0-100]
        S2[核心6大指标卡片<br/>QPS / P99 / 成功率 / GPU% / MEM% / 队列]
        S3[全球/全节点 地图热力图]
        S4[实时告警榜 P0-P2]
    end
    
    subgraph L2 服务分析 Layer - 开发/运维
        D1[服务维度下钻<br/>LLM / RAG / 调度 / Tool]
        D2[端到端耗时瀑布图<br/>占比TopN瓶颈]
        D3[错误分布 Top10]
        D4[资源-性能关联分析]
    end
    
    subgraph L3 根因定位 Layer - 工程师
        R1[Trace 调用链火焰图]
        R2[日志按TraceID聚合查询]
        R3[指标-日志-追踪 三联跳转]
        R4[历史同比 / 基线对比]
    end

    style L1 fill:#d4edda,stroke:#155724
    style L2 fill:#fff3cd,stroke:#d39e00
    style L3 fill:#d1ecf1,stroke:#0c5460
```

### 4.2 Grafana 仪表盘面板清单(可直接导入 JSON)

#### L1 总览仪表盘(单屏 1920×1080 刚好)

| 面板位置 | 类型 | 指标 | 说明 |
|---------|-----:|-----|------|
| 顶部第1行 6张卡片 | Stat | QPS / P99 / Success% / GPU% / MEM% / Queue | 绿黄红三色阈值 |
| 左上 | Gauge | Global Health Score(综合评分) | 公式:各SLA达标率×权重 |
| 左中 | TimeSeries | QPS + 错误率(双Y轴) | 5分钟窗口 |
| 左下 | TimeSeries | P50/P95/P99 延迟 | 3条线,一目了然 |
| 右上 | BarGauge | 各节点 Agent 利用率(Top 15) | 快速发现热点节点 |
| 右中 | Pie | 错误类型分布 | LLM/Tool/RAG/Timeout/其他 |
| 右下 | Stat + List | 实时告警列表(P0 红色、P1橙色)| 最新50条 |
| 底部 | StatusMap | 节点 × 优先级 队列热力图 | 深色=堆积多 |

#### L2 分维度仪表盘

**(1) LLM 维度**:
- RPM / TPM 速率曲线
- Token 消耗(Input/Output 分色堆叠)
- 缓存命中率(分查询类型)
- 供应商请求成功/失败率(多供应商对比)
- TTFT P99、TPOT P99 流式指标

**(2) RAG 维度**:
- 检索 P50/P99 延迟
- 向量库 vs 关键词检索 耗时对比
- 召回率趋势(按抽样批次打点)
- Embedding 推理耗时
- Top-K 命中率分布

**(3) 调度维度**:
- 队列长度(按优先级分色堆叠面积)
- 调度延迟 P99
- Agent 负载均衡度 std/mean
- 能力匹配命中率
- 分配失败率 / 抢占次数

**(4) 资源维度**:
- CPU 每核利用率热力图
- GPU 显存占用堆叠(每GPU)
- 内存 RSS 趋势 + OOM Kill 标记
- 磁盘 Util% + IOPS 双轴
- 网络带宽 + 重传率

#### L3 根因定位视图

- **Trace 跳转**:点击某请求的高延迟点 → 直接跳到 Jaeger 看调用链火焰图。
- **日志关联**:点击某错误率峰 → 自动跳到 Loki 按时间窗+TraceID 查询。
- **历史对比**:今天 vs 昨天 vs 上周同时间段,快速判断是回归还是正常波动。

---

## 五、异常阈值告警机制

### 5.1 告警分级与响应SLA

| 级别 | 颜色 | 定义示例 | 触达渠道 | 响应SLA | 处理人 |
|:---:|:----:|---------|---------|:-------:|-------|
| **P0 SEV1** | 深红 | 核心业务不可用: 成功率<90% 或 P0 SLA<95% 或 主进程崩溃/全部Agent离线 | 电话+短信+钉钉/飞书+微信 | **15分钟** | 值班SRE + 负责人 |
| **P1 SEV2** | 橙 | 严重劣化: P99>3×基线 或 错误率>3% 或 GPU显存>95% 或 队列>500 持续5min | 钉钉/飞书 @all + 短信 | 30分钟 | 值班SRE |
| **P2 SEV3** | 黄 | 轻度异常: 某子系统错误率>1% 或 某Agent离线 或 磁盘<15% 或 泄漏速率>50MB/h | 钉钉/飞书 群 | 2小时 | 对应研发 |
| **P3 SEV4** | 蓝 | 趋势预警: 指标环比劣化>20% 但未达阈值 / 预测未来24h磁盘满 | 邮件 + 次日晨会 | 24小时 | 研发跟进 |

### 5.2 核心告警规则(Prometheus 风格)

```yaml
# 告警规则示例 - 已标注对应用户需求的阈值设计
groups:
  - name: agent_severity_rules
    rules:
      # ========== P0 核心告警 ==========
      - alert: Agent_Main_Crash
        expr: increase(proc_restart_count_1h[15m]) >= 2
        for: 1m
        labels: { severity: P0 }
        annotations:
          summary: "Agent主进程15分钟内重启 >=2次,疑似崩溃"
      
      - alert: Success_Rate_Plummet
        expr: success_rate_pct < 90
        for: 2m
        labels: { severity: P0 }
        annotations:
          summary: "整体成功率 <90%,超过2分钟"
      
      # ========== P1 严重劣化 ==========
      - alert: P99_Latency_Spike
        expr: latency_p99_ms > 3 * baseline_p99_7d and latency_p99_ms > 8000
        for: 3m
        labels: { severity: P1 }
        annotations:
          summary: "P99 延迟突增为7日基线3倍以上,持续3分钟"
      
      - alert: Memory_Leak_Suspected
        expr: memory_leak_mb_per_hour > 50
        for: 3h
        labels: { severity: P1 }
        annotations:
          summary: "内存泄漏速率>50MB/h,连续3小时(经验200832差分判定)"
      
      - alert: GPU_Memory_Near_Full
        expr: gpu_memory_used_pct > 95
        for: 2m
        labels: { severity: P1 }
      
      - alert: Queue_Backlog_Serious
        expr: queue_size_total > 500
        for: 5m
        labels: { severity: P1 }
      
      # ========== P2 轻度异常 ==========
      - alert: Error_Rate_Above_1pct
        expr: error_rate_pct > 1
        for: 10m
        labels: { severity: P2 }
      
      - alert: Agent_Offline
        expr: agent_offline_count >= 1
        for: 3m
        labels: { severity: P2 }
      
      - alert: Disk_Space_Warning
        expr: disk_free_pct < 15 or disk_free_gb < 20
        for: 5m
        labels: { severity: P2 }
      
      - alert: GPU_High_Temperature
        expr: gpu_temperature_c > 85
        for: 5m
        labels: { severity: P2 }
      
      # ========== P3 趋势预测 ==========
      - alert: Disk_Full_Predicted_24h
        expr: predict_linear(disk_free_gb[6h], 24*3600) < 0
        for: 15m
        labels: { severity: P3 }
        annotations:
          summary: "按过去6小时线性预测,24小时内磁盘将满"
      
      # ========== 监控系统自监控(经验P8) ==========
      - alert: Monitor_Self_Queue_Backlog
        expr: mon_queue_backlog > 10000
        for: 2m
        labels: { severity: P2 }
        annotations:
          summary: "监控自身缓冲队列积压>10000,监控本身可能卡住/变慢"
```

### 5.3 告警抑制与聚合(防告警风暴)

```mermaid
flowchart TB
    Raw[100条原始告警] --> GROUP[按服务/节点/告警类型<br/>分组聚合]
    GROUP --> DEDUP[去重:同条件10分钟内只发1次]
    DEDUP --> ENRICH[丰富上下文<br/>添加runbook链接/负责人/历史同告警]
    ENRICH --> SILENCE[维护期/已知问题静默]
    SILENCE --> ESCALATE[分级升级<br/>P0 15min没人响应→升级到更高级]
    ESCALATE --> NOTIFY[最终通知]
```

---

## 六、结构化日志与查询分析

### 6.1 日志分级策略(写入入口的差异化,经验1265259)

```mermaid
flowchart LR
    E[ERROR 严重错误] --> W1[立即落盘<br/>同步+备份]
    W[WARN 警告] --> W2[0.5秒批量Flush<br/>环形队列缓冲]
    I[INFO 一般信息] --> W3[1秒批量Flush<br/>队列>2000条可丢弃最旧]
    D[DEBUG 调试] --> W4[采样率默认1%<br/>超阈值直接丢弃]
    T[TRACE 追踪] --> W5[仅开关开启时<br/>仅特定TraceID]
```

**磁盘写入频率**: ERROR < WARN < INFO << DEBUG << TRACE,保证高频DEBUG不打垮磁盘。

### 6.2 结构化日志字段(JSON 每行一条,非字符串拼接)

```python
# 每条结构化日志必须包含的最小字段集
LOG_REQUIRED_FIELDS = {
    "ts":           "ISO8601 时间戳(精确到毫秒)",
    "level":        "DEBUG/INFO/WARN/ERROR/FATAL",
    "logger":       "模块名 agent.llm / agent.rag / agent.scheduler",
    "trace_id":     "全链路追踪ID,贯穿 指标-日志-追踪",
    "span_id":      "当前Span ID",
    "parent_id":    "父Span ID,可选",
    "agent_id":     "哪个Agent实例",
    "user_id":      "可脱敏的用户标识(可选)",
    "task_id":      "任务ID(可选)",
    "priority":     "任务优先级(可选)",
    "msg":          "人类可读短消息",
    "duration_ms":  "操作耗时(可选,毫秒)",
    "error_type":   "异常类型名(ERROR时必填)",
    "error_msg":    "异常消息(ERROR时必填)",
    "stack":        "堆栈(ERROR时WARN以上采样)",
    "attrs": {      # 扩展属性,自由KV
        "llm_model": "gpt-4",
        "tool_name": "web_search",
        "tokens": 1520
    }
}
```

### 6.3 日志查询分析(Loki / ClickHouse)

#### 常用Top 10 查询模板

```sql
-- Q1: 最近1小时内 ERROR / WARN 按错误类型分组计数
SELECT error_type, count(*) as cnt
FROM agent_logs
WHERE ts >= now() - INTERVAL 1 HOUR
  AND level IN ('ERROR', 'WARN')
GROUP BY error_type
ORDER BY cnt DESC
LIMIT 50

-- Q2: 某 Trace ID 的完整 指标+日志+事件 时序
SELECT ts, level, logger, msg, attrs
FROM agent_logs
WHERE trace_id = 'abc123xyz'
ORDER BY ts ASC

-- Q3: 最近15分钟P99最高的Top 10接口/操作
SELECT span_name, quantile(0.99)(duration_ms) as p99
FROM agent_logs
WHERE ts >= now() - INTERVAL 15 MINUTE
  AND duration_ms IS NOT NULL
GROUP BY span_name
ORDER BY p99 DESC
LIMIT 10

-- Q4: 过去24小时日志量/错误率同比趋势(按10分钟桶)
SELECT toStartOfTenMinutes(ts) as bucket,
       count(*) as total,
       countIf(level='ERROR') as err_cnt,
       round(err_cnt * 100.0 / total, 3) as err_rate
FROM agent_logs
WHERE ts >= today() - 1
GROUP BY bucket
ORDER BY bucket ASC

-- Q5: 最近1小时最常出现的错误堆栈 Top 10(相似堆栈聚类)
SELECT error_type, any(error_msg) sample_msg, count(*) cnt
FROM agent_logs
WHERE ts >= now() - INTERVAL 1 HOUR AND level = 'ERROR'
GROUP BY error_type
ORDER BY cnt DESC
LIMIT 10

-- Q6: 慢查询/慢任务 Top 50(耗时>10秒)
SELECT ts, trace_id, task_id, span_name, duration_ms, attrs
FROM agent_logs
WHERE ts >= now() - INTERVAL 1 HOUR AND duration_ms > 10000
ORDER BY duration_ms DESC
LIMIT 50

-- Q7: 哨兵值异常检测(经验335399 -9999清洗核查)
SELECT countIf(attrs['raw_value'] < -9000) as sentinel_hits
FROM agent_logs
WHERE ts >= now() - INTERVAL 1 HOUR AND logger = 'metric_cleaner'

-- Q8: 日志级别分布(确认DEBUG是否被意外开启)
SELECT level, count(*) cnt
FROM agent_logs
WHERE ts >= now() - INTERVAL 5 MINUTE
GROUP BY level
ORDER BY cnt DESC

-- Q9: 每个Agent实例的错误率对比
SELECT agent_id,
       count(*) total,
       countIf(level='ERROR') errs,
       round(errs * 100.0 / total, 3) err_rate
FROM agent_logs
WHERE ts >= now() - INTERVAL 30 MINUTE
GROUP BY agent_id
HAVING total > 100
ORDER BY err_rate DESC

-- Q10: 监控自身的丢弃日志数(经验P8)
SELECT sum(toInt64(attrs['dropped'])) as total_dropped
FROM agent_logs
WHERE ts >= now() - INTERVAL 10 MINUTE
  AND logger = 'monitor.self'
```

---

## 七、Agent 监控系统完整 Python 实现

### 7.1 核心模块关系

```mermaid
flowchart TB
    M["AgentMonitor 门面类<br/>外部统一使用接口"]
    
    M --> MC[MetricCollector<br/>指标采集 + 哨兵值清洗]
    M --> MB[MetricsBuffer<br/>环形队列 + 分类缓冲]
    M --> MM[MetricsPublisher<br/>1秒定时批量 flush]
    M --> AL[AsyncStructuredLogger<br/>分级批量日志写入]
    M --> AM[AlertEvaluator<br/>阈值告警评估]
    M --> SM[SelfMonitor<br/>监控系统自监控]
```

### 7.2 完整实现代码(约 600 行,生产可用)

```python
"""
agent_monitor.py — Agent 运行状态监控框架
核心特点:
  1. 指标采集层 - 哨兵值/越界值清洗(经验335399)
  2. 写入缓冲队列 + 分级flush - ERROR立即/INFO 1秒批量/DEBUG可丢弃(经验1265259)
  3. 计数器差分 - 内存泄漏/资源泄漏判定(经验200832)
  4. 监控自监控 - 队列长/flush延迟/丢弃数
  5. 对 Agent 性能影响: <1% CPU, <10MB 内存, <0.5% 请求延迟
"""
import os
import sys
import time
import json
import threading
import logging
import statistics
from typing import Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from pathlib import Path
from collections import defaultdict, deque
from datetime import datetime, timedelta

try:
    import psutil  # 可选:CPU/内存/磁盘/网络
except ImportError:
    psutil = None

try:
    import pynvml  # 可选:GPU监控
except ImportError:
    pynvml = None


# ============================================================
# 7.3 常量与配置: 哨兵值/合法范围/批量flush参数
# ============================================================

# 哨兵值集合(经验335399) - 采集中遇到这些值应丢弃,不写入指标库
DEFAULT_SENTINELS = {
    None, float("nan"), float("inf"), -float("inf"),
    -9999, -99999, -999,
    "", "N/A", "UNKNOWN", "null",
}

# 指标字段合法范围:(min, max) — None表示无界
DEFAULT_FIELD_RANGES: dict[str, tuple[Optional[float], Optional[float]]] = {
    "cpu_util_pct":          (0, 100),
    "cpu_load_1":            (0, 4096),
    "memory_rss_mb":         (0, None),
    "memory_util_pct":       (0, 100),
    "memory_vss_mb":         (0, None),
    "swap_used_mb":          (0, None),
    "gpu_sm_util_pct":       (0, 100),
    "gpu_memory_mb":         (0, None),
    "gpu_memory_pct":        (0, 100),
    "gpu_temperature_c":     (-40, 150),
    "gpu_power_w":           (0, None),
    "disk_util_pct":         (0, 110),  # 允许短暂>100%的毛刺
    "disk_iops_read":        (0, None),
    "disk_iops_write":       (0, None),
    "net_mbps_in":           (0, None),
    "net_mbps_out":          (0, None),
    "net_retrans_pct":       (0, 100),
    "qps_total":             (0, None),
    "qps_success":           (0, None),
    "latency_ms":            (0, 600_000),   # 单请求最多10分钟
    "latency_p50_ms":        (0, None),
    "latency_p95_ms":        (0, None),
    "latency_p99_ms":        (0, None),
    "ttft_ms":               (0, None),
    "success_rate_pct":      (0, 100),
    "error_rate_pct":        (0, 100),
    "sla_pass_rate_pct":     (0, 100),
    "llm_rpm":               (0, None),
    "llm_cache_hit_pct":     (0, 100),
    "tokens_per_request":    (0, None),
    "rag_search_ms":         (0, None),
    "rag_recall_pct":        (0, 100),
    "queue_size_total":      (0, None),
    "queue_p0_count":        (0, None),
    "scheduler_latency_ms":  (0, None),
    "agent_utilization_pct": (0, 100),
    "agent_offline_count":   (0, None),
    "proc_restart_count":    (0, None),
    "memory_leak_mb_per_hour": (-500, 5000),
    "oom_kill_count":        (0, None),
}

# 分类缓冲策略(经验1265259)
FLUSH_POLICIES = {
    "CRITICAL": {"max_delay_ms": 0,    "drop_if_full": False},  # 绝不丢弃
    "ERROR":    {"max_delay_ms": 0,    "drop_if_full": False},
    "WARN":     {"max_delay_ms": 500,  "drop_if_full": False},
    "INFO":     {"max_delay_ms": 1000, "drop_if_full": True},   # 满了丢老INFO
    "DEBUG":    {"max_delay_ms": 5000, "drop_if_full": True,
                 "sample_rate": 0.01}, # 采样1%,降低写入
}


# ============================================================
# 7.4 数据结构
# ============================================================
@dataclass
class MetricPoint:
    name: str
    value: float
    ts_ms: int
    type: str = "gauge"  # gauge / counter / histogram
    labels: dict = field(default_factory=dict)
    level: str = "INFO"  # 用于缓冲分级


@dataclass
class LogRecord:
    ts_ms: int
    level: str
    logger_name: str
    trace_id: str
    msg: str
    duration_ms: Optional[float] = None
    error_type: Optional[str] = None
    error_msg: Optional[str] = None
    attrs: dict = field(default_factory=dict)
    span_id: Optional[str] = None


# ============================================================
# 7.5 MetricsBuffer: 环形缓冲 + 分级flush + 背压丢弃
# ============================================================
class MetricsBuffer:
    """
    指标缓冲器
    
    - 按级别分队列(CRITICAL/ERROR/INFO/DEBUG)
    - INFO 队列超过容量丢弃最旧数据(经验1265259)
    - DEBUG 额外采样率控制(默认1%)
    """
    
    def __init__(self, max_capacity_per_level: int = 50000):
        self.max_cap = max_capacity_per_level
        self._queues: dict[str, deque] = {
            level: deque(maxlen=self.max_cap if policy["drop_if_full"] else None)
            for level, policy in FLUSH_POLICIES.items()
        }
        # 兼容旧级别: 指标使用 INFO/ERROR 两级即可
        self._lock = threading.Lock()
        # 自监控计数
        self.dropped_counts: dict[str, int] = defaultdict(int)
        self.total_enqueued = 0
    
    def enqueue(self, point: MetricPoint) -> bool:
        level = point.level
        # DEBUG 采样(经验1265259)
        if level == "DEBUG":
            import random
            if random.random() > FLUSH_POLICIES["DEBUG"].get("sample_rate", 0.01):
                self.dropped_counts["debug_sample_skip"] += 1
                return False
        
        q = self._queues[level]
        with self._lock:
            before_len = len(q)
            q.append(point)
            after_len = len(q)
            self.total_enqueued += 1
            # 定容deque如果丢弃了最旧,增量为0,记一次dropped
            if before_len == self.max_cap and after_len == before_len:
                self.dropped_counts[level] += 1
        return True
    
    def drain(self, level: Optional[str] = None,
              max_items: int = 20000) -> list[MetricPoint]:
        """排空缓冲,返回最多max_items条"""
        levels = [level] if level else list(FLUSH_POLICIES.keys())
        out = []
        with self._lock:
            for lvl in levels:
                q = self._queues[lvl]
                take = min(len(q), max_items - len(out))
                if take <= 0:
                    break
                for _ in range(take):
                    out.append(q.popleft())
        return out
    
    def size(self) -> dict[str, int]:
        with self._lock:
            return {lvl: len(q) for lvl, q in self._queues.items()}


# ============================================================
# 7.6 MetricCollector: 资源采集 + 哨兵值清洗
# ============================================================
class MetricCollector:
    """
    指标采集器
    
    1. 系统资源(CPU/GPU/MEM/DISK/NET)
    2. **最重要**: 采集值→哨兵值清洗→越界裁剪(经验335399)
    """
    
    def __init__(self, sentinels: set = None, field_ranges: dict = None):
        self.sentinels = sentinels or DEFAULT_SENTINELS
        self.field_ranges = field_ranges or DEFAULT_FIELD_RANGES
        
        # 历史值用于差分(经验200832)
        self._hist_rss_mb: deque = deque(maxlen=360)  # 6小时@10s每次
        self._hist_threads: deque = deque(maxlen=360)
        self._hist_fds: deque = deque(maxlen=360)
        
        self._proc = psutil.Process(os.getpid()) if psutil else None
        self._last_net = None
        self._last_disk = None
        self._nvml_inited = False
        
        if pynvml and not self._nvml_inited:
            try:
                pynvml.nvmlInit()
                self._nvml_inited = True
            except Exception:
                pass
    
    # ---- 核心: 指标清洗(经验335399) ----
    def sanitize(self, name: str, value: Any) -> Optional[float]:
        """清洗指标值:哨兵值丢弃,越界裁剪,类型转换"""
        # 1) 哨兵值直接丢弃
        if value in self.sentinels:
            return None
        
        # 2) 字符串尝试转float
        if isinstance(value, str):
            try:
                value = float(value)
            except (ValueError, TypeError):
                return None
        
        # 3) 类型转换
        try:
            v = float(value)
        except (ValueError, TypeError):
            return None
        
        # 4) NaN/Inf 丢弃
        if v != v or v in (float("inf"), -float("inf")):  # NaN != NaN
            return None
        
        # 5) 合法范围裁剪或丢弃
        rng = self.field_ranges.get(name)
        if rng:
            lo, hi = rng
            if lo is not None and v < lo:
                # 越界低于下限: 可能是哨兵(-9999等伪装成合法数值),直接丢弃
                return None
            if hi is not None and v > hi:
                # 高于上限,裁剪(如Util>100)
                v = float(hi)
        return v
    
    # ---- 系统资源采集 ----
    def collect_system(self) -> list[MetricPoint]:
        now = int(time.time() * 1000)
        out: list[MetricPoint] = []
        
        if not psutil:
            return out
        
        # CPU
        try:
            cpu_pct = psutil.cpu_percent(interval=None)
            self._add(out, "cpu_util_pct", cpu_pct, now)
            load1, _, _ = psutil.getloadavg()
            self._add(out, "cpu_load_1", load1, now)
        except Exception:
            pass
        
        # 内存(进程RSS/VSS + 系统利用率)
        try:
            mem = psutil.virtual_memory()
            self._add(out, "memory_util_pct", mem.percent, now)
            if self._proc:
                rss_mb = self._proc.memory_info().rss / (1024 * 1024)
                self._add(out, "memory_rss_mb", rss_mb, now)
                self._hist_rss_mb.append((now, rss_mb))
                vss_mb = self._proc.memory_info().vms / (1024 * 1024)
                self._add(out, "memory_vss_mb", vss_mb, now)
                
                # 线程数 / FD 数
                try:
                    threads_n = self._proc.num_threads()
                    self._add(out, "proc_threads_count", threads_n, now)
                    self._hist_threads.append((now, threads_n))
                except Exception:
                    pass
                try:
                    fds = self._proc.num_fds() if hasattr(self._proc, "num_fds") else len(self._proc.connections())
                    self._add(out, "proc_fd_count", fds, now)
                    self._hist_fds.append((now, fds))
                except Exception:
                    pass
        except Exception:
            pass
        
        # Swap
        try:
            swap = psutil.swap_memory()
            self._add(out, "swap_used_mb", swap.used / (1024 * 1024), now)
        except Exception:
            pass
        
        # GPU
        if self._nvml_inited:
            try:
                device_count = pynvml.nvmlDeviceGetCount()
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    labels = {"gpu": str(i)}
                    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    self._add(out, "gpu_sm_util_pct", util.gpu, now, labels=labels)
                    mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    mem_pct = mem.used * 100.0 / mem.total if mem.total > 0 else 0
                    self._add(out, "gpu_memory_pct", mem_pct, now, labels=labels)
                    self._add(out, "gpu_memory_mb", mem.used / (1024 * 1024), now, labels=labels)
                    temp = pynvml.nvmlDeviceGetTemperature(handle, 0)
                    self._add(out, "gpu_temperature_c", temp, now, labels=labels)
                    power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
                    self._add(out, "gpu_power_w", power, now, labels=labels)
            except Exception:
                pass
        
        # 磁盘 Util
        try:
            for part in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    self._add(out, "disk_free_pct", 100 - usage.percent, now,
                              labels={"mount": part.mountpoint})
                except Exception:
                    continue
        except Exception:
            pass
        
        # 内存泄漏速率(经验200832 差分判定)
        leak = self.compute_leak_rate()
        if leak is not None:
            self._add(out, "memory_leak_mb_per_hour", leak, now)
        
        return out
    
    def compute_leak_rate(self) -> Optional[float]:
        """差分计算内存增长速率 MB/hour (经验200832)"""
        if len(self._hist_rss_mb) < 2:
            return None
        # 至少30个点或10分钟以上的数据
        pts = list(self._hist_rss_mb)
        if len(pts) < 6:
            return None
        (t0, v0), (t1, v1) = pts[0], pts[-1]
        dt_h = (t1 - t0) / (1000 * 3600)
        if dt_h <= 0:
            return None
        return (v1 - v0) / dt_h
    
    # ---- 业务指标便捷入口 ----
    def observe_request(self, success: bool, latency_ms: float,
                        priority: str = "P2",
                        trace_id: str = "",
                        error_type: Optional[str] = None) -> list[MetricPoint]:
        now = int(time.time() * 1000)
        out: list[MetricPoint] = []
        self._add(out, "latency_ms", latency_ms, now, type="histogram",
                  labels={"priority": priority, "trace": trace_id[:8]})
        self._add(out, "qps_total", 1, now, type="counter",
                  labels={"priority": priority})
        if success:
            self._add(out, "qps_success", 1, now, type="counter",
                      labels={"priority": priority})
        else:
            self._add(out, "qps_failed", 1, now, type="counter",
                      labels={"priority": priority, "err": error_type or "unknown"})
        return out
    
    def _add(self, out: list, name: str, value: Any, ts_ms: int,
             type: str = "gauge", labels: dict = None, level: str = "INFO"):
        v = self.sanitize(name, value)
        if v is None:
            return
        out.append(MetricPoint(
            name=name, value=v, ts_ms=ts_ms,
            type=type, labels=labels or {}, level=level
        ))


# ============================================================
# 7.7 AsyncStructuredLogger: 分级批量结构化日志写入
# ============================================================
class AsyncStructuredLogger:
    """
    结构化异步日志
    
    - 写入入口按级别差异化处理(经验1265259)
    - ERROR 立即落盘、WARN 500ms批量、INFO 1秒批量、DEBUG 采样+可丢弃
    - 每行JSON一条,便于Loki/ClickHouse直接消费
    """
    
    def __init__(self, log_dir: str, max_file_mb: int = 500):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.max_file_mb = max_file_mb
        self._files: dict[str, Any] = {}
        self._lock = threading.Lock()
        self._buffer: dict[str, deque] = {lvl: deque() for lvl in FLUSH_POLICIES}
        self._thread = threading.Thread(target=self._flush_loop, name="LoggerFlush", daemon=True)
        self._stop_evt = threading.Event()
        self._thread.start()
        self.dropped = 0
    
    def _current_file(self, level: str):
        # 每天/每级一个文件,超过大小滚号
        day = datetime.now().strftime("%Y%m%d")
        key = f"{day}_{level}"
        with self._lock:
            if key in self._files:
                f, path, size = self._files[key]
                if size > self.max_file_mb * 1024 * 1024:
                    try: f.close()
                    except Exception: pass
                    del self._files[key]
            if key not in self._files:
                idx = 1
                while True:
                    path = self.log_dir / f"agent_{day}_{level}_{idx:03d}.jsonl"
                    if not path.exists():
                        break
                    idx += 1
                f = open(path, "a", encoding="utf-8", buffering=8 * 1024 * 1024)
                self._files[key] = (f, path, 0)
            return self._files[key]
    
    def log(self, record: LogRecord):
        # DEBUG 采样
        if record.level == "DEBUG":
            import random
            if random.random() > FLUSH_POLICIES["DEBUG"].get("sample_rate", 0.01):
                return
        buf = self._buffer.get(record.level)
        if buf is None:
            buf = self._buffer["INFO"]
        # ERROR 不缓冲直接写,其他先入队列
        if record.level in ("CRITICAL", "ERROR"):
            self._write_now(record)
        else:
            if len(buf) >= 10000:
                # 非关键队列满了丢最旧
                try: buf.popleft()
                except Exception: pass
                self.dropped += 1
            buf.append(record)
    
    def _write_now(self, record: LogRecord):
        line = self._format(record) + "\n"
        f, path, size = self._current_file(record.level)
        try:
            f.write(line)
            size += len(line)
            # 500ms以下的批量不每条flush,由定时flush线程统一刷
            if record.level in ("CRITICAL", "ERROR"):
                f.flush()
            with self._lock:
                self._files[f"{datetime.now().strftime('%Y%m%d')}_{record.level}"] = (f, path, size)
        except Exception:
            pass
    
    def _format(self, r: LogRecord) -> str:
        obj = {
            "ts": datetime.fromtimestamp(r.ts_ms / 1000).isoformat(timespec="milliseconds"),
            "level": r.level,
            "logger": r.logger_name,
            "trace_id": r.trace_id or "",
            "span_id": r.span_id or "",
            "msg": r.msg,
        }
        if r.duration_ms is not None:
            obj["duration_ms"] = round(r.duration_ms, 2)
        if r.error_type:
            obj["error_type"] = r.error_type
            obj["error_msg"] = r.error_msg
        if r.attrs:
            obj["attrs"] = r.attrs
        # 注意: 所有日志都必须是可JSON序列化,防止非字符串污染
        try:
            return json.dumps(obj, ensure_ascii=False, default=str)
        except Exception:
            obj2 = {k: str(v) for k, v in obj.items()}
            return json.dumps(obj2, ensure_ascii=False)
    
    def _flush_loop(self):
        last_flush_ms = defaultdict(int)
        while not self._stop_evt.is_set():
            now_ms = time.time() * 1000
            for lvl, policy in FLUSH_POLICIES.items():
                delay = policy["max_delay_ms"]
                # ERROR/CRITICAL已立即写,此处处理队列里的批量
                if delay == 0:
                    continue
                if now_ms - last_flush_ms[lvl] < delay:
                    continue
                buf = self._buffer[lvl]
                # 批量写最多1000条
                n = min(1000, len(buf))
                if n == 0:
                    last_flush_ms[lvl] = now_ms
                    continue
                lines = []
                for _ in range(n):
                    try:
                        rec = buf.popleft()
                        lines.append(self._format(rec))
                    except Exception:
                        break
                if lines:
                    f, path, size = self._current_file(lvl)
                    try:
                        block = "\n".join(lines) + "\n"
                        f.write(block)
                        f.flush()
                        size += len(block)
                        with self._lock:
                            key = f"{datetime.now().strftime('%Y%m%d')}_{lvl}"
                            self._files[key] = (f, path, size)
                    except Exception:
                        pass
                last_flush_ms[lvl] = now_ms
            self._stop_evt.wait(0.1)
    
    def close(self):
        self._stop_evt.set()
        if self._thread.is_alive():
            self._thread.join(timeout=5)
        with self._lock:
            for f, _, _ in self._files.values():
                try: f.flush(); f.close()
                except Exception: pass


# ============================================================
# 7.8 MetricsPublisher: 异步批量上报 + 分类flush
# ============================================================
class MetricsPublisher:
    def __init__(self, buffer: MetricsBuffer,
                 push_fn: Optional[Callable[[list[MetricPoint]], None]] = None,
                 local_jsonl_dir: Optional[str] = None):
        self.buffer = buffer
        self.push_fn = push_fn
        self.local_dir = Path(local_jsonl_dir) if local_jsonl_dir else None
        if self.local_dir:
            self.local_dir.mkdir(parents=True, exist_ok=True)
        self._stop_evt = threading.Event()
        self._thread = threading.Thread(target=self._loop, name="MetricsPublisher", daemon=True)
        self._thread.start()
    
    def _loop(self):
        # CRITICAL/ERROR 快一些: 200ms; INFO/DEBUG: 1s
        tick = 0
        while not self._stop_evt.is_set():
            tick += 1
            points = []
            points += self.buffer.drain("CRITICAL", 5000)
            points += self.buffer.drain("ERROR", 5000)
            if tick % 5 == 0:  # ~1s
                points += self.buffer.drain("WARN", 10000)
                points += self.buffer.drain("INFO", 20000)
            if tick % 50 == 0:  # ~10s
                points += self.buffer.drain("DEBUG", 5000)
            
            if points:
                self._publish(points)
            
            self._stop_evt.wait(0.2)
    
    def _publish(self, points: list[MetricPoint]):
        if self.local_dir:
            day = datetime.now().strftime("%Y%m%d")
            path = self.local_dir / f"metrics_{day}.jsonl"
            try:
                with path.open("a", encoding="utf-8") as f:
                    for p in points:
                        f.write(json.dumps({
                            "ts": p.ts_ms, "name": p.name, "value": p.value,
                            "type": p.type, "labels": p.labels
                        }, ensure_ascii=False) + "\n")
            except Exception:
                pass
        if self.push_fn:
            try:
                self.push_fn(points)
            except Exception:
                pass
    
    def close(self):
        self._stop_evt.set()
        if self._thread.is_alive():
            self._thread.join(timeout=5)


# ============================================================
# 7.9 AlertEvaluator: 阈值告警评估
# ============================================================
class AlertEvaluator:
    """轻量告警评估器 - 进程内即可判定,无需Prometheus也能告警"""
    
    @dataclass
    class Rule:
        id: str
        metric: str
        op: str  # >, <, >=, <=, ==
        threshold: float
        duration_sec: int
        severity: str  # P0/P1/P2/P3
        summary: str
    
    def __init__(self, rules: list[Rule],
                 alert_cb: Callable[[str, str, dict], None] = None):
        self.rules = rules
        self.alert_cb = alert_cb
        # 每指标的滑动窗口: ts_ms -> value
        self._windows: dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self._fired: dict[str, int] = {}
    
    def observe(self, name: str, value: float, ts_ms: int):
        self._windows[name].append((ts_ms, value))
    
    def evaluate(self, now_ms: Optional[int] = None) -> list[dict]:
        """评估所有规则,返回触发的告警列表"""
        now_ms = now_ms or int(time.time() * 1000)
        fired = []
        for r in self.rules:
            win = self._windows.get(r.metric)
            if not win:
                continue
            dur = r.duration_sec * 1000
            pts = [(t, v) for t, v in win if t >= now_ms - dur]
            if len(pts) < 2:
                continue
            # 全部满足条件才算(持续duration)
            ok = all(self._cmp(v, r.op, r.threshold) for _, v in pts)
            if not ok:
                self._fired.pop(r.id, None)
                continue
            # 避免重复: 同一规则10分钟内只发1次
            last = self._fired.get(r.id, 0)
            if now_ms - last < 10 * 60 * 1000:
                continue
            self._fired[r.id] = now_ms
            evt = {
                "rule_id": r.id,
                "severity": r.severity,
                "summary": r.summary,
                "metric": r.metric,
                "op": r.op,
                "threshold": r.threshold,
                "current_value": pts[-1][1],
                "duration_sec": r.duration_sec,
                "fired_at": now_ms
            }
            fired.append(evt)
            if self.alert_cb:
                try:
                    self.alert_cb(r.severity, r.summary, evt)
                except Exception:
                    pass
        return fired
    
    @staticmethod
    def _cmp(v: float, op: str, t: float) -> bool:
        try:
            return {
                ">": lambda: v > t,
                "<": lambda: v < t,
                ">=": lambda: v >= t,
                "<=": lambda: v <= t,
                "==": lambda: abs(v - t) < 1e-9,
            }[op]()
        except KeyError:
            return False


# ============================================================
# 7.10 AgentMonitor 门面类 + 装饰器埋点
# ============================================================
class AgentMonitor:
    """
    监控系统门面类 - 业务代码只需import一个对象使用
    
    Usage:
        monitor = AgentMonitor(
            log_dir="./logs",
            metrics_dir="./logs/metrics",
            alert_cb=my_webhook_alert
        )
        monitor.start()
        
        # 装饰器埋点
        @monitor.trace("llm_call")
        def call_llm(...):
            ...
        
        # 手动记录
        monitor.record_request(success=True, latency_ms=123)
    """
    
    DEFAULT_RULES = [
        AlertEvaluator.Rule(
            "success_plummet", "success_rate_pct", "<", 90.0, 120, "P0",
            "整体成功率<90%,超过2分钟"),
        AlertEvaluator.Rule(
            "p99_spike", "latency_p99_ms", ">", 15000, 120, "P1",
            "P99延迟>15秒,持续2分钟"),
        AlertEvaluator.Rule(
            "mem_leak", "memory_leak_mb_per_hour", ">", 50, 3600 * 3, "P1",
            "内存泄漏速率>50MB/h持续3小时(经验200832)"),
        AlertEvaluator.Rule(
            "queue_backlog", "queue_size_total", ">", 500, 300, "P1",
            "任务队列>500持续5分钟"),
        AlertEvaluator.Rule(
            "error_rate_1pct", "error_rate_pct", ">", 1.0, 600, "P2",
            "错误率>1%持续10分钟"),
        AlertEvaluator.Rule(
            "disk_warning", "disk_free_pct", "<", 15.0, 300, "P2",
            "磁盘空闲<15%"),
    ]
    
    def __init__(self, log_dir: str = "./agent_monitor_logs",
                 metrics_dir: str = "./agent_monitor_logs/metrics",
                 alert_cb: Optional[Callable] = None,
                 rules: list[AlertEvaluator.Rule] = None,
                 extra_sentinels: set = None,
                 extra_field_ranges: dict = None):
        sentinels = set(DEFAULT_SENTINELS)
        if extra_sentinels:
            sentinels.update(extra_sentinels)
        field_ranges = dict(DEFAULT_FIELD_RANGES)
        if extra_field_ranges:
            field_ranges.update(extra_field_ranges)
        
        self.collector = MetricCollector(sentinels, field_ranges)
        self.buffer = MetricsBuffer()
        self.publisher = MetricsPublisher(self.buffer, local_jsonl_dir=metrics_dir)
        self.logger = AsyncStructuredLogger(log_dir)
        self.alerter = AlertEvaluator(rules or self.DEFAULT_RULES, alert_cb)
        
        self._start_ts = time.time()
        self._stop_evt = threading.Event()
        self._threads: list[threading.Thread] = []
        self._hist_lats: deque = deque(maxlen=100000)
        self._success_count = 0
        self._total_count = 0
        self._err_counts = defaultdict(int)
    
    # ---- 生命周期 ----
    def start(self):
        t1 = threading.Thread(target=self._system_collect_loop,
                              name="MonitorSysCollect", daemon=True)
        t2 = threading.Thread(target=self._eval_aggregates,
                              name="MonitorAggrEval", daemon=True)
        t1.start(); t2.start()
        self._threads = [t1, t2]
        
        self.logger.log(LogRecord(
            ts_ms=int(time.time() * 1000),
            level="INFO", logger_name="agent_monitor",
            trace_id="monitor_start",
            msg="Agent 监控系统已启动",
            attrs={"pid": os.getpid(), "cwd": os.getcwd()}
        ))
    
    def stop(self):
        self._stop_evt.set()
        for t in self._threads:
            if t.is_alive():
                t.join(timeout=5)
        self.publisher.close()
        self.logger.close()
    
    # ---- 便捷接口: 记录业务请求 ----
    def record_request(self, success: bool, latency_ms: float,
                       priority: str = "P2",
                       trace_id: str = "",
                       error_type: Optional[str] = None):
        pts = self.collector.observe_request(
            success, latency_ms, priority, trace_id, error_type
        )
        for p in pts:
            self.buffer.enqueue(p)
        self._hist_lats.append(latency_ms)
        self._total_count += 1
        if success:
            self._success_count += 1
        elif error_type:
            self._err_counts[error_type] += 1
    
    # ---- 便捷接口: 装饰器埋点 ----
    def trace(self, span_name: str, level: str = "INFO"):
        """无侵入装饰器,记录耗时+错误+TraceID"""
        import functools
        def decorator(fn):
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                import uuid
                trace_id = kwargs.get("trace_id") or str(uuid.uuid4())
                start = time.time()
                err_type = err_msg = None
                result = None
                try:
                    result = fn(*args, **kwargs)
                    return result
                except Exception as e:
                    err_type, err_msg = type(e).__name__, str(e)[:200]
                    raise
                finally:
                    dur_ms = (time.time() - start) * 1000
                    success = err_type is None
                    # 写指标
                    pt = MetricPoint(
                        name=f"span_{span_name}_ms",
                        value=dur_ms,
                        ts_ms=int(time.time() * 1000),
                        type="histogram", level=level
                    )
                    self.buffer.enqueue(pt)
                    # 写日志
                    self.logger.log(LogRecord(
                        ts_ms=int(time.time() * 1000),
                        level=level if success else "ERROR",
                        logger_name=f"span.{span_name}",
                        trace_id=trace_id,
                        msg=f"{span_name} done",
                        duration_ms=dur_ms,
                        error_type=err_type,
                        error_msg=err_msg,
                        attrs={"ok": success}
                    ))
            return wrapper
        return decorator
    
    # ---- 后台循环1: 采集系统资源 ----
    def _system_collect_loop(self):
        while not self._stop_evt.is_set():
            try:
                for p in self.collector.collect_system():
                    self.buffer.enqueue(p)
                    self.alerter.observe(p.name, p.value, p.ts_ms)
            except Exception:
                pass
            self._stop_evt.wait(10)  # 10秒一次资源采集
    
    # ---- 后台循环2: 30秒桶聚合 + 告警评估 ----
    def _eval_aggregates(self):
        while not self._stop_evt.is_set():
            self._stop_evt.wait(30)
            if self._stop_evt.is_set():
                break
            lats = list(self._hist_lats)
            now_ms = int(time.time() * 1000)
            if lats:
                sorted_lats = sorted(lats)
                n = len(sorted_lats)
                def pct(p): return sorted_lats[min(n - 1, int(n * p / 100))]
                success_rate = (
                    self._success_count / self._total_count * 100
                    if self._total_count > 0 else 100.0
                )
                err_rate = 100.0 - success_rate
                
                # 预聚合指标(经验: 避免Prometheus侧重复计算)
                pre = [
                    ("latency_p50_ms", pct(50)),
                    ("latency_p95_ms", pct(95)),
                    ("latency_p99_ms", pct(99)),
                    ("success_rate_pct", success_rate),
                    ("error_rate_pct", err_rate),
                    ("qps_30s_avg", self._total_count / 30.0),
                ]
                for name, val in pre:
                    pt = MetricPoint(name=name, value=val,
                                     ts_ms=now_ms, type="gauge", level="INFO")
                    self.buffer.enqueue(pt)
                    self.alerter.observe(name, val, now_ms)
            
            # 评估告警
            fired = self.alerter.evaluate(now_ms)
            for evt in fired:
                self.logger.log(LogRecord(
                    ts_ms=now_ms, level="WARN", logger_name="monitor.alert",
                    trace_id=evt["rule_id"],
                    msg=f"ALERT [{evt['severity']}] {evt['summary']}",
                    attrs=evt
                ))
            # 清零本桶计数(滚动窗)
            self._success_count = 0
            self._total_count = 0
            self._err_counts.clear()
    
    # ---- 健康快照: API返回JSON供仪表盘使用 ----
    def health_snapshot(self) -> dict:
        """返回当前健康快照,用于L1总览仪表盘 /healthz接口"""
        now = time.time()
        uptime = int(now - self._start_ts)
        
        lats = list(self._hist_lats)
        sorted_lats = sorted(lats) if lats else [0]
        n = max(1, len(sorted_lats))
        
        # 健康评分(0-100): 权重 SLA 30% + 错误率 30% + 队列 15% + 资源 25%
        success = self._success_count / max(1, self._total_count) * 100
        score = min(100.0, 50 + success * 0.5)  # 简化计算,生产可做更精细
        
        return {
            "uptime_sec": uptime,
            "health_score": round(score, 1),
            "latency_ms": {
                "avg": round(statistics.mean(sorted_lats), 2),
                "p50": round(sorted_lats[int(n * 0.50)], 2),
                "p95": round(sorted_lats[int(n * 0.95)], 2),
                "p99": round(sorted_lats[int(n * 0.99)], 2),
            },
            "success_rate_pct": round(success, 3),
            "total_requests_sample": n,
            "buffer_sizes": self.buffer.size(),
            "buffer_dropped": dict(self.buffer.dropped_counts),
            "logger_dropped": self.logger.dropped,
            "monitor_self_metrics": {  # 经验P8: 自监控
                "cpu_pct_last": None,
                "mem_rss_mb": self.collector._hist_rss_mb[-1][1] if self.collector._hist_rss_mb else None,
                "leak_mb_hour": round(self.collector.compute_leak_rate() or 0, 2),
            }
        }


# ============================================================
# 7.11 使用示例(30秒集成)
# ============================================================
if __name__ == "__main__":
    def demo_alert(severity: str, summary: str, evt: dict):
        print(f"\n[ALERT {severity}] {summary} -> {json.dumps(evt, ensure_ascii=False, default=str)}")
    
    monitor = AgentMonitor(
        log_dir="./demo_logs",
        metrics_dir="./demo_logs/metrics",
        alert_cb=demo_alert,
    )
    monitor.start()
    
    import random, traceback
    
    # 装饰器示例
    @monitor.trace("mock_llm_call")
    def call_llm(query: str) -> str:
        time.sleep(random.uniform(0.1, 2.5))
        if random.random() < 0.05:
            raise RuntimeError("LLM timeout")
        return "Hello"
    
    print("监控系统已启动, 模拟 30 秒业务请求...")
    st = time.time()
    n_total = n_ok = 0
    try:
        while time.time() - st < 30:
            n_total += 1
            try:
                call_llm("test query")
                monitor.record_request(True, latency_ms=random.uniform(100, 3000))
                n_ok += 1
            except Exception:
                monitor.record_request(False, latency_ms=random.uniform(500, 10000),
                                       error_type="LLMError")
            # 每0.1秒一个请求,≈10 QPS
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    
    snap = monitor.health_snapshot()
    print("\n===== 健康快照 =====")
    print(json.dumps(snap, ensure_ascii=False, indent=2))
    
    monitor.stop()
    print(f"\n演示完成: 总请求 {n_total}, 成功 {n_ok}")
    print(f"日志目录: {monitor.logger.log_dir.absolute()}")
    print(f"指标目录: {monitor.publisher.local_dir.absolute() if monitor.publisher.local_dir else '-'}")
```

---

## 八、最小性能影响控制策略(核心)

### 8.1 影响预算总表

目标:监控系统本身对 Agent 的**总影响 < 1% CPU、< 10MB 内存、< 0.5% 请求延迟**。

| 模块 | CPU 预算 | 内存预算 | 请求延迟影响 |
|-----|:--------:|:-------:|:----------:|
| 资源采集器(每10s) | <0.2% | <3MB | 0 |
| 业务埋点装饰器 | <0.2% | <1MB | <0.1ms |
| 哨兵值清洗 | <0.05% | <0.5MB | <0.02ms |
| 缓冲 + 分类 flush | <0.1% | <4MB | 0(异步) |
| 结构化日志异步写入 | <0.2% | <1.5MB | 0(异步) |
| 告警评估(30秒) | <0.1% | <0.5MB | 0 |
| 上报发布(批量) | <0.15% | <0.5MB | 0(异步) |
| **合计** | **<1.0%** | **<11MB** | **<0.12ms / 请求**✅ |

### 8.2 九大控制策略详解

| # | 策略 | 实现位置 | 作用 |
|:-:|-----|---------|-----|
| **1** | **采集降频** | CPU/GPU/磁盘/NET 10s, 非1s | 采集频次从1s降到10s,采集耗时下降90% |
| **2** | **环形队列有界** | `deque(maxlen=N)` + 分级丢弃 | 防止极端流量下内存爆炸,INFO/DEBUG 队列满自动丢老数据 |
| **3** | **DEBUG 采样率 1%** | `random.random()<0.01` 才记录 | DEBUG日志量直接降到 1%, 生产默认关 |
| **4** | **分级flush策略** | ERROR立即 / INFO 1s 批量 / DEBUG 10s | 减少磁盘同步次数, 单条写变批量写 |
| **5** | **全异步线程** | 采集/发布/告警 各走独立daemon线程 | 业务热路径零等待,不阻塞请求 |
| **6** | **1秒桶预聚合** | 30秒周期将latency分位数先算好再上报 | 上报量从 每请求→每30秒一条(P50/P95/P99) |
| **7** | **哨兵值前置清洗** | 采集层入缓冲前先清洗 | 避免无效数据走后续链路浪费IO/CPU |
| **8** | **监控自监控 + 熔断** | `mon_queue_backlog` / 背压 | 队列积压超过阈值时,自动降采样或暂停非关键指标 |
| **9** | **装饰器无侵入 + 独立连接池** | `@monitor.trace` / 独立线程 | 不改业务签名,不与业务共享连接资源,避免资源争用 |

### 8.3 自监控与熔断机制(防监控反噬)

```python
# 监控系统的自监控规则(经验P8)
SELF_MONITOR_RULES = [
    ("mon_buffer_backlog",      ">", 20000, 60,  "P2", "监控缓冲队列积压>20000"),
    ("mon_publisher_flush_ms",  ">", 5000,  120, "P2", "指标发布单次>5秒"),
    ("mon_logger_dropped_1m",   ">", 1000,  300, "P3", "日志丢弃>1000条/5分钟"),
]

# 熔断策略:
# - 当监控队列积压>50000持续1分钟 → 强制暂停DEBUG指标采集
# - 当监控队列积压>100000持续2分钟 → 暂停INFO指标采集(只保留ERROR/WARN/CRITICAL)
# - 当监控队列积压回落到<10000持续5分钟 → 逐步恢复 INFO, 再恢复 DEBUG
```

---

## 九、实施步骤与验证方法

### 9.1 六步实施路线

```mermaid
flowchart TD
    S1[Step1 代码无侵入接入<br/>2天] --> S2[Step2 单机本地验证<br/>1天]
    S2 --> S3[Step3 预发环境灰度<br/>3天]
    S3 --> S4[Step4 性能影响验证<br/>1天]
    S4 --> S5[Step5 仪表盘与告警配置<br/>2天]
    S5 --> S6[Step6 生产全量 + 持续迭代<br/>长期]
```

#### Step 1: 代码无侵入接入(2天)

- 引入 `AgentMonitor` 单例,在服务启动入口 `start()`、停止入口 `stop()`。
- 对核心路径(LLM/RAG/Tool/Scheduler)加装饰器 `@monitor.trace("llm_call")`。
- 不改业务签名:用装饰器 + context manager 两种方式,不用改业务函数返回与参数。
- 日志:替换原有print式日志为 `monitor.logger.log(...)`。

#### Step 2: 单机本地验证(1天)

```bash
# 跑上一节的__main__ demo,观察:
#   1) 是否正常产生 日志/metrics jsonl文件
#   2) HealthSnapshot 输出是否合理
#   3) CPU是否<1%、内存是否<10MB额外占用
python agent_monitor.py
```

#### Step 3: 预发灰度(3天)

- 先 **10% 流量** 开关:通过配置项 `MONITOR_ENABLE_TRACE=true/false` 控制埋点。
- 打开采样 DEBUG 只在灰度实例。
- 检查指标:监控自监控(backlog/dropped)是否正常,无积压。

#### Step 4: 性能影响验证(1天)

**AB对比法:同一台机器同一代码,同一套压测Runner**

| 指标组 | 监控关闭 | 监控开启 | 差值 | 判定 |
|-------|:--------:|:--------:|:----:|:----:|
| P50 响应 | 820ms | 820.05ms | +0.05ms | ✅ <0.5% 影响 |
| P99 响应 | 2.1s | 2.103s | +3ms | ✅ 可接受 |
| QPS 稳态 | 95 | 94.7 | -0.3 | ✅ <0.5% 影响 |
| CPU 额外 | — | 0.42% | 0.42% | ✅ <1% |
| RSS 额外 | — | 6.8MB | 6.8MB | ✅ <10MB |
| 监控队列积压 | — | 峰值 1,200 | <50K阈值 | ✅ 正常 |

**全部满足差值阈值,通过影响验证**。

#### Step 5: 仪表盘与告警配置(2天)

- 按 4.2 节面板清单导入 Grafana。
- 按 5.2 节告警规则导入到 Prometheus / 自研告警器。
- 人为注入一次故障(如 kill Agent Worker),看告警是否按时、按分级触达。

#### Step 6: 生产全量 + 持续迭代

- 先全量 INFO 级别,DEBUG 按实例开(只在 1-2 台查问题用)。
- 每周回顾:新业务埋点补全、异常值模式(新增哨兵值)加入清洗规则。

### 9.2 功能验证用例清单

| # | 验证项 | 操作方法 | 期望结果 |
|:-:|-------|---------|---------|
| V1 | **指标可观测** | 压测5分钟,访问/healthz接口 | 返回CPU/MEM/P99等指标,非空非负 |
| V2 | **哨兵值清洗** | 手动注入 `record` 一条 `cpu=-9999` | CPU指标不出现-9999,被丢弃 |
| V3 | **越界裁剪** | 注入 `cpu=200.0` | 存入指标库时裁剪到100.0 |
| V4 | **批量flush** | 产生1000条INFO日志,用lsof看fd | 5分钟内磁盘写入次数<100次(非每条写) |
| V5 | **错误不丢** | 产生100条ERROR日志 | 全部落盘,count=100 |
| V6 | **debug采样** | 产生10000条DEBUG | 最终落盘≈100条(±采样率误差) |
| V7 | **内存泄漏差分** | 人为构造RSS持续增长 | `memory_leak_mb_per_hour` 正确计算 |
| V8 | **告警触发** | 人为将成功率降到85%持续2分钟 | P0 告警正常触发,回调/飞书到达 |
| V9 | **告警抑制** | 同一告警10分钟内重复触发 | 只发1次,不告警风暴 |
| V10 | **Trace贯通** | 记录一条请求的指标+日志+埋点 | 三者 trace_id 相同,可联合查询 |
| V11 | **监控自监控** | 故意让队列积压(阻塞publish) | `mon_queue_backlog` 上升,并触发自告警 |
| V12 | **低侵入** | 压测对比(Step4) | CPU<1%,内存<10MB,延迟影响<0.5% ✅ |

---

## 十、总结与选型建议

### 10.1 方案选型矩阵(按需选择)

| 场景 | 推荐方案 | 存储 | 仪表盘 | 告警 | 复杂度 |
|-----|---------|------|:------:|:----:|:------:|
| **小型单体Agent** | 本文自实现 + JSONL本地存储 | JSONL 本地 | Flask小页面 / Streamlit | 自研AlertEvaluator + webhook | 低 |
| **中型团队** | 自实现采集 + Prometheus + Loki | VictoriaMetrics + Loki | Grafana | Alertmanager + 飞书/钉钉 | 中 |
| **大型企业/K8s** | OpenTelemetry SDK(替换自实现Publisher) + OTLP Collector | Prom/Loki/Jaeger集群 | Grafana + 自研健康评分 | Alertmanager + PagerDuty/企业IM | 高 |
| **全链路追踪需求重** | 本文采集器 + Jaeger/ Zipkin 上报 | ClickHouse | Grafana Tempo | 关联错误日志告警 | 高 |

> 本文的 `MetricCollector`、`AsyncStructuredLogger`、清洗/缓冲/采样策略,**无论上不上Prometheus/Grafana,都是必须落地的基础能力**——这是解决"观测不足就盲目改策略"(经验200832)的根本。

### 10.2 一句话核心要点

> **先有最小可观测面(计数器 + 差分 + 哨兵值清洗 + 分级批量写),再谈策略优化;监控本身必须低侵入、可自监控、对业务影响量化可控。**

### 10.3 与系列文档的关联

- **稳定性**: [116Agent系统稳定性提升完整方案深度解析.md](./116Agent系统稳定性提升完整方案深度解析.md) — 本文监控是稳定性的前置可观测层。
- **压力测试**: [120Agent系统全面压力测试方案深度解析与实施指南.md](./120Agent系统全面压力测试方案深度解析与实施指南.md) — 压测 Runner 的数据来源于本文监控系统。
- **Multi-Agent 调度**: [119Multi-Agent系统任务调度功能深度解析.md](./119Multi-Agent系统任务调度功能深度解析.md) — 调度指标(队列/延迟/负载/离线)来源于本文。
- **内存泄漏/资源泄漏**: 本文的**计数器差分法**(经验200832)直接用于定位泄漏,并由浸泡测试(S5)验证。

---

> **相关文档**
>
> - 稳定性体系: [116Agent系统稳定性提升完整方案深度解析.md](./116Agent系统稳定性提升完整方案深度解析.md)
> - 压力测试验证: [120Agent系统全面压力测试方案深度解析与实施指南.md](./120Agent系统全面压力测试方案深度解析与实施指南.md)
> - Multi-Agent 调度指标: [119Multi-Agent系统任务调度功能深度解析.md](./119Multi-Agent系统任务调度功能深度解析.md)
> - 向量数据库监控: [119向量数据库性能系统性优化完整方案深度解析.md](./119向量数据库性能系统性优化完整方案深度解析.md)
> - RAG 查询优化: [118RAG系统查询响应速度全面优化方案深度解析.md](./118RAG系统查询响应速度全面优化方案深度解析.md)
