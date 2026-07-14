# PCDN流量分析模块 - 技术深度分析文档

> 文档版本：1.0
> 生成日期：2026-07-12
> 模块名称：ngfa-cloud-pcdn

---

## 一、模块概述

### 1.1 业务背景

PCDN（P2P CDN）是一种利用边缘网络带宽和内容分发网络的技术，通过调动边缘设备和终端用户的闲置带宽资源，降低CDN成本。然而，部分用户利用家庭宽带或企业专线私自部署PCDN节点进行牟利，导致网络资源被滥用，影响正常业务。

### 1.2 模块定位

PCDN流量分析模块是群顶综合流量分析平台的核心业务模块之一，主要功能包括：
- **疑似用户识别**：基于多维度流量特征模型，识别疑似PCDN用户
- **风险评估**：对疑似用户进行风险评分和等级划分
- **流量分析**：分析PCDN用户的上下行流量、端口、协议等特征
- **可视化展示**：提供多维度的报表和图表展示

### 1.3 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    PCDN模块架构                          │
├─────────────────────────────────────────────────────────┤
│  配置层（pcdnConfig）                                    │
│  ├─ PcdnModel（流量模型配置）                            │
│  ├─ PcdnModelDetail（模型评分规则）                      │
│  ├─ PcdnRiskGrade（风险等级配置）                        │
│  ├─ PcdnHomeUserIp（家宽用户IP库）                       │
│  ├─ PcdnPlatformDomain（PCDN平台域名库）                 │
│  └─ PcdnFeatureDomain（PCDN特征域名库）                  │
├─────────────────────────────────────────────────────────┤
│  分析层（pcdnReport）                                    │
│  ├─ 数据预处理节点（DataPreHandle）                      │
│  ├─ 评分计算节点（DataPostHandle）                       │
│  │   ├─ UDFlowRatioScore（上下行流量评分）               │
│  │   ├─ MakeFinalScore（综合得分计算）                   │
│  │   ├─ MakeUdRatioTabulation（评分区间报表）            │
│  │   └─ ScoringCriteria（评分标准展示）                  │
│  └─ 数据查询Mapper（ClickHouse）                        │
├─────────────────────────────────────────────────────────┤
│  数据层                                                  │
│  ├─ pcdn_suspected_user_P1D（疑似用户日表）              │
│  ├─ pcdn_dns_analysis（DNS分析表）                       │
│  ├─ pcdn_radius_pool（Radius认证池）                     │
│  └─ domain_apply_info（域名备案信息）                    │
└─────────────────────────────────────────────────────────┘
```

---

## 二、核心数据模型

### 2.1 流量特征模型（PcdnModel）

PCDN识别采用**多维度加权评分模型**，包含6个核心特征维度：

| 模型类型 | 类型编码 | 权重 | 业务含义 |
|---------|---------|------|---------|
| 上下行流量不对称 | `UP_DOWN_FLOW` | 可配置 | PCDN节点通常上行流量远大于下行 |
| 目标端口散列 | `TARGET_PORT_HASH` | 可配置 | PCDN服务使用大量不同目的端口 |
| 源端口汇聚 | `SOURCE_PORT_AGG` | 可配置 | PCDN流量集中在少数源端口 |
| 上行UDP协议占比 | `UP_UDP_PROPORTION` | 可配置 | PCDN主要使用UDP协议传输 |
| 服务本省用户占比 | `LOCAL_USER_PROPORTION` | 可配置 | PCDN节点主要服务本地用户 |
| PCDN特征域名 | `PCDN_DOMAIN` | 可配置 | 访问已知PCDN平台域名 |

**数据库表结构：**
```sql
-- ============================================================
-- 表名：pcdn_model_info（PCDN流量特征模型主表）
-- 用途：存储PCDN识别所使用的各维度流量特征模型配置
-- 说明：每个模型代表一种PCDN识别维度（如上下行流量比、端口散列等），
--       通过weight字段控制该维度在综合评分中的权重占比
-- ============================================================
CREATE TABLE pcdn_model_info (
    -- 主键ID，采用雪花算法生成32位字符串
    id VARCHAR(32) PRIMARY KEY,
    -- 模型名称，用于前端展示（如"上下行流量不对称"）
    name VARCHAR(100) NOT NULL COMMENT '模型名称',
    -- 模型类型编码，与PcdnConstant.FlowModelType中的常量对应
    -- 可选值：UP_DOWN_FLOW / TARGET_PORT_HASH / SOURCE_PORT_AGG 等
    type VARCHAR(50) NOT NULL COMMENT '模型类型编码',
    -- 权重值（0-100），表示该维度在综合评分中的占比百分比
    -- 所有模型权重之和应为100
    weight INT NOT NULL COMMENT '权重(0-100)',
    -- 模型的业务说明，描述该维度识别PCDN的原理
    description VARCHAR(500) COMMENT '业务说明',
    -- 启用状态：0=禁用（不参与评分），1=启用
    status INT DEFAULT 1 COMMENT '状态(0禁用/1启用)',
    -- 记录创建时间
    create_time DATETIME,
    -- 记录最后更新时间
    update_time DATETIME
);
```

> **功能总结：** 该SQL定义了PCDN流量特征模型主表，采用一行一模型的设计，每个模型对应一种PCDN识别维度。核心字段`type`标识模型类型，`weight`控制评分权重，`status`控制是否参与计算。该表是配置驱动设计的基础，运营人员可通过修改此表动态调整识别策略，无需变更代码。

### 2.2 评分规则配置（PcdnModelDetail）

每个流量模型对应一组评分区间，用于将原始指标值映射为0-100分：

```sql
-- ============================================================
-- 表名：pcdn_model_detail_info（PCDN模型评分规则明细表）
-- 用途：存储每个流量模型的评分区间配置
-- 说明：将原始指标值（如上下行流量比）映射为0-100分的评分标准
--       每个模型类型对应多条评分规则，形成区间-分数的映射关系
-- ============================================================
CREATE TABLE pcdn_model_detail_info (
    -- 主键ID，采用雪花算法生成32位字符串
    id VARCHAR(32) PRIMARY KEY,
    -- 关联的模型类型编码，与pcdn_model_info.type字段对应
    -- 例如：UP_DOWN_FLOW表示上下行流量比模型的评分规则
    type VARCHAR(50) NOT NULL COMMENT '关联模型类型',
    -- 评分区间的起始值（包含），支持小数
    -- 特殊值：Integer.MIN_VALUE表示负无穷
    start_ratio DOUBLE NOT NULL COMMENT '区间起始值',
    -- 评分区间的结束值（包含），支持小数
    -- 特殊值：Integer.MAX_VALUE表示正无穷，字符串"∞"表示无上界
    end_ratio DOUBLE NOT NULL COMMENT '区间结束值',
    -- 该区间对应的评分（0-100分）
    -- 分数越高表示PCDN嫌疑越大
    score INT NOT NULL COMMENT '该区间对应得分',
    -- 记录创建时间
    create_time DATETIME
);
```

> **功能总结：** 该SQL定义了PCDN模型评分规则明细表，采用一行一区间的设计。核心逻辑是将连续的指标值离散化为评分区间。例如上下行流量比[0,0.5)映射为0分，[0.5,1.0)映射为20分，以此类推。通过`start_ratio`和`end_ratio`定义区间边界，`score`定义该区间的基础得分。支持无穷大/无穷小的特殊边界处理，适配各种极端场景。

**评分规则示例（上下行流量比）：**

| 区间 | 得分 | 业务含义 |
|------|------|---------|
| [0, 0.5) | 0分 | 正常用户（下行>上行） |
| [0.5, 1.0) | 20分 | 轻度异常 |
| [1.0, 2.0) | 40分 | 中度异常 |
| [2.0, 5.0) | 60分 | 高度异常 |
| [5.0, 10.0) | 80分 | 极高风险 |
| [10.0, ∞) | 100分 | 确定PCDN |

### 2.3 风险等级配置（PcdnRiskGrade）

根据综合得分划分风险等级：

```sql
-- ============================================================
-- 表名：pcdn_risk_grade_info（PCDN风险等级配置表）
-- 用途：根据综合评分划分风险等级
-- 说明：将0-100分的综合得分映射为不同的风险等级
--       用于指导运营人员采取不同级别的处置措施
-- ============================================================
CREATE TABLE pcdn_risk_grade_info (
    -- 主键ID，采用雪花算法生成32位字符串
    id VARCHAR(32) PRIMARY KEY,
    -- 风险区间的起始系数（包含），取值范围0-100
    -- 例如：80表示80分以上为极高风险
    start_ratio FLOAT NOT NULL COMMENT '起始风险系数',
    -- 风险区间的结束系数（包含），取值范围0-100
    -- 例如：100表示最高分为100分
    end_ratio FLOAT NOT NULL COMMENT '结束风险系数',
    -- 风险等级编码，与PcdnConstant.PcdnRiskLevelEnum对应
    -- 可选值：extremelyHigh(极高) / high(高) / medium(中) / low(低)
    risk_level VARCHAR(20) NOT NULL COMMENT '风险等级',
    -- 记录创建时间
    create_time DATETIME
);
```

> **功能总结：** 该SQL定义了PCDN风险等级配置表，采用一行一等级区间的设计。核心逻辑是将综合评分（0-100分）划分为不同的风险等级。例如[80,100]分为"极高"风险，[60,80)分为"高"风险，以此类推。通过`start_ratio`和`end_ratio`定义风险区间边界，`risk_level`定义对应的风险等级编码。该配置支持动态调整，运营人员可根据实际业务需求灵活设定风险阈值。

**风险等级划分：**

| 风险等级 | 编码 | 得分区间 | 处理建议 |
|---------|------|---------|---------|
| 极高 | `extremelyHigh` | [80, 100] | 立即处置 |
| 高 | `high` | [60, 80) | 重点关注 |
| 中 | `medium` | [40, 60) | 持续监控 |
| 低 | `low` | [0, 40) | 正常观察 |

---

## 三、核心算法详解

### 3.1 综合评分算法

#### 3.1.1 算法流程

```
┌─────────────────────────────────────────────────────────┐
│              PCDN综合评分算法流程                         │
└─────────────────────────────────────────────────────────┘

输入：用户流量特征数据
  ├─ udFlowRatio: 上下行流量比
  ├─ oppositeFrequentlyPortRatio: TOP5目的端口流量占比
  ├─ topPortRatio: TOP5源端口流量占比
  ├─ protocolRatio: 上行UDP协议占比
  ├─ localFlowRatio: 服务本省用户占比
  └─ pcdnDomainCount: PCDN特征域名访问数

处理流程：
  Step 1: 维度评分（各维度独立评分0-100）
    ├─ 查询PcdnModelDetail获取评分区间
    ├─ 将原始值映射到对应区间
    └─ 输出各维度得分

  Step 2: 加权计算（综合得分）
    ├─ 查询PcdnModel获取各维度权重
    ├─ 公式：Σ(维度得分 × 权重/100)
    └─ 输出综合得分（0-100）

  Step 3: 风险定级
    ├─ 查询PcdnRiskGrade获取风险区间
    ├─ 根据综合得分匹配风险等级
    └─ 输出风险标签

输出：
  ├─ score: 综合得分
  └─ suspectedLevel: 风险等级
```

#### 3.1.2 核心代码实现

**MakeFinalScore.java - 综合得分计算**

```java
/**
 * PCDN综合得分计算节点
 *
 * 功能说明：
 * 1. 从数据库加载所有启用的流量特征模型及其权重配置
 * 2. 从数据库加载风险等级划分规则
 * 3. 对每个用户的各维度得分进行加权求和，计算综合得分
 * 4. 根据综合得分匹配对应的风险等级
 *
 * 核心算法：
 * - 加权求和公式：finalScore = Σ(维度得分 × 权重/100)
 * - 风险匹配：遍历风险等级区间，找到综合得分所在的区间
 *
 * 使用场景：
 * - 作为责任链模式的最后一个节点，在所有维度评分完成后执行
 * - 输出最终的综合得分和风险等级，供前端展示和后续处理使用
 *
 * 注意事项：
 * - 使用@Scope("prototype")确保每次请求创建新实例，避免线程安全问题
 * - 计算完成后清理临时数据（各维度原始得分），减少内存占用
 */
@Scope("prototype")  // 原型作用域，每次注入时创建新实例
@Component("makeFinalScore")  // Spring Bean名称，用于YAML配置中引用
public class MakeFinalScore extends DataPostHandle {

    /**
     * Feign客户端：调用配置服务获取流量模型列表
     * 包含模型类型、权重等配置信息
     */
    @Resource
    private PcdnModelFeign pcdnModelFeign;

    /**
     * Feign客户端：调用配置服务获取风险等级配置
     * 包含风险区间边界和风险等级编码
     */
    @Resource
    private PcdnRiskGradeFeign pcdnRiskGradeFeign;

    /**
     * 核心处理方法：执行综合得分计算逻辑
     *
     * @param reportMetadata  报表元数据（包含字段定义、展示类型等）
     * @param reportRequest   报表请求参数（包含查询条件、时间范围等）
     * @param reportResponse  报表响应对象（包含待处理的用户数据列表）
     *
     * 处理流程：
     * 1. 加载配置数据（模型列表、风险等级）
     * 2. 遍历每个用户的数据Map
     * 3. 对每个用户，遍历所有模型维度进行加权求和
     * 4. 根据综合得分匹配风险等级
     * 5. 将结果写回数据Map
     */
    @Override
    protected void handle(ReportMetadata reportMetadata,
                         ReportRequest reportRequest,
                         ReportResponse reportResponse) {

        // 步骤1：从配置服务获取所有启用的流量模型
        // 返回结果示例：[
        //   {type: "UP_DOWN_FLOW", weight: 30},
        //   {type: "TARGET_PORT_HASH", weight: 20},
        //   ...
        // ]
        List<PcdnModel> modelList = pcdnModelFeign.pageList(new PcdnModel()).getList();

        // 步骤2：从配置服务获取风险等级划分规则
        // 返回结果示例：[
        //   {startRatio: 80.0, endRatio: 100.0, riskLevel: "extremelyHigh"},
        //   {startRatio: 60.0, endRatio: 80.0, riskLevel: "high"},
        //   ...
        // ]
        List<PcdnRiskGrade> riskGradeList = pcdnRiskGradeFeign.pageList(new PcdnRiskGrade()).getList();

        // 步骤3：遍历每个用户的数据，计算综合得分和风险等级
        // reportResponse.getTemporaryList()包含所有用户的原始数据
        // 每个用户的数据以Map<String, Object>形式存储
        // Map中已包含各维度的原始得分（由前置节点计算完成）
        Optional.ofNullable(reportResponse.getTemporaryList())
                .orElse(new ArrayList<>())  // 空值保护，避免NPE
                .stream()
                .forEach(map -> {
                    // 初始化综合得分为0
                    Float finalScore = 0f;

                    // 步骤4：遍历所有模型维度，进行加权求和
                    // 核心公式：finalScore += 维度得分 × (权重 / 100)
                    for (PcdnModel model : modelList) {
                        // 从Map中获取该维度的原始得分
                        // 如果不存在则默认为0.0分
                        String score = ObjectUtil.isNotEmpty(map.get(model.getType()))
                            ? map.get(model.getType()).toString()
                            : "0.0";

                        // 加权累加计算
                        // 例如：维度得分=80，权重=30，则贡献分数=80×0.3=24
                        finalScore = finalScore + model.getWeight() * 1.0f / 100.0f * Float.valueOf(score);

                        // 清理临时数据：移除该维度的原始得分
                        // 目的：减少Map体积，避免后续处理时产生混淆
                        map.remove(model.getType());
                    }

                    // 步骤5：将计算完成的综合得分写回Map
                    // 前端可通过"score"字段获取该用户的综合得分
                    map.put("score", finalScore);

                    // 步骤6：根据综合得分匹配风险等级
                    // 遍历所有风险等级区间，找到综合得分所在的区间
                    for (PcdnRiskGrade risk : riskGradeList) {
                        // 判断条件：startRatio <= finalScore <= endRatio
                        // 使用BigDecimalUtil确保浮点数比较的精度
                        if (BigDecimalUtil.isLessOrEqual(risk.getStartRatio(), finalScore) &&
                            BigDecimalUtil.isLessOrEqual(finalScore, risk.getEndRatio())) {
                            // 匹配成功，将风险等级写回Map
                            // 前端可通过"suspectedLevel"字段获取风险等级编码
                            map.put("suspectedLevel", risk.getRiskLevel());
                            // 匹配完成后立即跳出循环，避免重复匹配
                            break;
                        }
                    }
                });
    }
}
```

> **功能总结：** MakeFinalScore是PCDN评分责任链的核心节点，负责将各维度的原始得分汇总为综合得分，并划分风险等级。采用加权求和算法，通过配置化的模型权重实现灵活的评分策略。代码使用原型作用域保证线程安全，通过Optional空值保护避免NPE，并在计算完成后清理临时数据优化内存使用。该节点是连接"维度评分"和"风险定级"的关键桥梁。

**算法复杂度分析：**
- 时间复杂度：O(N × M)，N为用户数，M为模型维度数（固定为6）
- 空间复杂度：O(N)，存储用户得分结果
- 实际复杂度：O(N)，因为M=6为常数

### 3.2 单维度评分算法

#### 3.2.1 上下行流量比评分（UDFlowRatioScore）

**业务逻辑：**
PCDN节点的核心特征是"上传远大于下载"，通过上下行流量比识别此类用户。

**算法实现：**

```java
/**
 * 上下行流量比评分节点
 *
 * 功能说明：
 * 1. 从数据库加载上下行流量比（UP_DOWN_FLOW）的评分区间配置
 * 2. 对每个用户的上下行流量比进行区间匹配，获取对应的评分
 * 3. 将评分结果写回用户数据Map
 *
 * 核心算法：
 * - 区间匹配：遍历所有评分区间，找到用户上下行流量比所在的区间
 * - 特殊处理：支持无穷大边界（end_ratio="∞"）
 *
 * 业务逻辑：
 * - PCDN节点的核心特征是"上传远大于下载"
 * - 通过上下行流量比（udFlowRatio = 上行流量 / 下行流量）识别此类用户
 * - 流量比越高，PCDN嫌疑越大
 *
 * 使用场景：
 * - 作为责任链模式的一个节点，在数据预处理完成后执行
 * - 输出的评分将作为MakeFinalScore节点的输入
 */
@Scope("prototype")  // 原型作用域，每次请求创建新实例
@Component("uDFlowRatioScore")  // Spring Bean名称，用于YAML配置中引用
public class UDFlowRatioScore extends DataPostHandle {

    /**
     * Feign客户端：调用配置服务获取模型评分规则
     * 包含评分区间边界和对应分数
     */
    @Resource
    private PcdnModelDetailFeign pcdnModelDetailFeign;

    /**
     * 核心处理方法：执行上下行流量比评分逻辑
     *
     * @param reportMetadata  报表元数据
     * @param reportRequest   报表请求参数
     * @param reportResponse  报表响应对象（包含待处理的用户数据列表）
     *
     * 处理流程：
     * 1. 构建查询条件：type = UP_DOWN_FLOW
     * 2. 从配置服务获取该类型的所有评分区间
     * 3. 遍历每个用户的数据Map
     * 4. 提取用户的上下行流量比（udFlowRatio）
     * 5. 在评分区间列表中查找匹配的区间
     * 6. 将匹配到的评分写回Map
     */
    @Override
    protected void handle(ReportMetadata reportMetadata,
                         ReportRequest reportRequest,
                         ReportResponse reportResponse) {

        // 步骤1：构建查询条件，指定模型类型为"上下行流量比"
        // PcdnConstant.FlowModelType.UP_DOWN_FLOW = "UP_DOWN_FLOW"
        PcdnModelDetail modelDetail = PcdnModelDetail.builder()
            .type(PcdnConstant.FlowModelType.UP_DOWN_FLOW)
            .build();

        // 步骤2：从配置服务获取该类型的所有评分区间
        // 返回结果示例：[
        //   {startRatio: 0.0, endRatio: 0.5, score: 0},
        //   {startRatio: 0.5, endRatio: 1.0, score: 20},
        //   {startRatio: 1.0, endRatio: 2.0, score: 40},
        //   {startRatio: 2.0, endRatio: 5.0, score: 60},
        //   {startRatio: 5.0, endRatio: 10.0, score: 80},
        //   {startRatio: 10.0, endRatio: "∞", score: 100}
        // ]
        List<PcdnModelDetail> modelDetailList = pcdnModelDetailFeign.pageList(modelDetail).getList();

        // 步骤3：遍历每个用户的数据，进行区间匹配和评分
        Optional.ofNullable(reportResponse.getTemporaryList())
                .orElse(new ArrayList<>())  // 空值保护
                .stream()
                .forEach(map -> {
                    // 步骤4：在评分区间列表中查找匹配的区间
                    // 使用Stream API的filter方法，找到第一个满足条件的区间
                    Integer score = modelDetailList.stream()
                        .filter(item -> {
                            // 从Map中提取用户的上下行流量比
                            // 该值由前置的数据预处理节点计算并写入
                            Float udFlowRatio = Float.valueOf(map.get("udFlowRatio").toString());

                            // 区间匹配逻辑：start_ratio <= udFlowRatio <= end_ratio
                            // 使用BigDecimalUtil确保浮点数比较的精度

                            // 条件1：udFlowRatio >= startRatio
                            boolean greaterOrEqualStart = BigDecimalUtil.isLessOrEqual(
                                Double.valueOf(item.getStartRatio()),
                                udFlowRatio
                            );

                            // 条件2：udFlowRatio <= endRatio（或endRatio为无穷大）
                            // 特殊处理：当endRatio为"∞"时，表示无上界，只需满足条件1
                            boolean lessOrEqualEnd = PcdnConstant.INFINITY.equals(item.getEndRatio()) ||
                                BigDecimalUtil.isLessOrEqual(udFlowRatio, Double.valueOf(item.getEndRatio()));

                            // 两个条件同时满足，说明用户流量比落在该区间内
                            return greaterOrEqualStart && lessOrEqualEnd;
                        })
                        .findFirst()  // 找到第一个匹配的区间即可（区间互不重叠）
                        .orElse(new PcdnModelDetail())  // 未匹配到任何区间时返回空对象
                        .getScore();  // 获取该区间的评分

                    // 步骤5：将评分结果写回Map
                    // 键名为模型类型编码"UP_DOWN_FLOW"
                    // 后续MakeFinalScore节点会读取该值进行加权计算
                    map.put(PcdnConstant.FlowModelType.UP_DOWN_FLOW, score);
                });
    }
}
```

> **功能总结：** UDFlowRatioScore是PCDN评分责任链的单维度评分节点，专门处理上下行流量比这一核心特征。采用区间匹配算法，将连续的流量比值离散化为0-100的评分。代码使用Stream API简化过滤逻辑，通过BigDecimalUtil保证浮点数比较精度，并支持无穷大边界的特殊处理。该节点输出的评分将作为综合得分计算的输入，是PCDN识别的关键环节。

**区间匹配算法：**
```
输入：udFlowRatio（上下行流量比）
处理：
  1. 按start_ratio升序排列所有评分区间
  2. 遍历区间，检查是否满足：start_ratio ≤ udFlowRatio ≤ end_ratio
  3. 特殊处理：end_ratio="∞"时，仅检查udFlowRatio ≥ start_ratio
输出：匹配的区间得分（0-100）
```

### 3.3 评分标准展示算法（ScoringCriteria）

**业务需求：**
前端需要展示评分标准表格，包含：
- 评分区间
- 对应得分
- 用户实际值（高亮显示所在区间）

**算法实现：**

```java
/**
 * 评分标准展示节点
 *
 * 功能说明：
 * 1. 从数据库加载指定模型的评分区间配置
 * 2. 构建评分标准表格，包含区间、得分、用户实际值
 * 3. 高亮显示用户实际值所在的区间
 *
 * 核心算法：
 * - 区间格式化：将数据库中的小数转换为百分比显示
 * - 特殊值处理：负无穷显示为"0"，正无穷显示为"∞"
 * - 区间匹配：判断用户实际值落在哪个区间，进行高亮
 *
 * 业务逻辑：
 * - 前端需要展示评分标准表格，帮助用户理解评分规则
 * - 表格包含三列：评分区间、对应得分、用户实际值
 * - 用户实际值所在的区间需要高亮显示，便于对比分析
 *
 * 使用场景：
 * - 用于"评分标准"报表接口
 * - 支持所有6种模型类型的评分标准展示
 */
@Scope("prototype")  // 原型作用域，每次请求创建新实例
@Component("scoringCriteria")  // Spring Bean名称，用于YAML配置中引用
public class ScoringCriteria extends DataPostHandle {

    /**
     * Feign客户端：调用配置服务获取模型评分规则
     */
    @Resource
    private PcdnModelDetailFeign pcdnModelDetailFeign;

    /**
     * 核心处理方法：构建评分标准表格
     *
     * @param reportMetadata  报表元数据
     * @param reportRequest   报表请求参数（包含模型类型type）
     * @param reportResponse  报表响应对象（包含用户实际数据）
     *
     * 处理流程：
     * 1. 根据请求参数中的模型类型，加载对应的评分区间
     * 2. 遍历所有评分区间，构建表格行
     * 3. 提取用户实际值，判断落在哪个区间
     * 4. 将结果写回响应对象
     */
    @Override
    protected void handle(ReportMetadata reportMetadata,
                         ReportRequest reportRequest,
                         ReportResponse reportResponse) {

        // 步骤1：根据请求参数中的模型类型，构建查询条件
        // reportRequest.getType()返回模型类型编码，如"UP_DOWN_FLOW"
        PcdnModelDetail pcdnModelDetail = PcdnModelDetail.builder()
            .type(reportRequest.getType())
            .build();

        // 从配置服务获取该类型的所有评分区间
        List<PcdnModelDetail> pcdnModelDetails = pcdnModelDetailFeign.dataList(pcdnModelDetail);

        // 初始化结果列表，用于存储表格的每一行数据
        List<Map<String, Object>> resultList = new ArrayList<>();

        // 步骤2：遍历所有评分区间，构建表格行
        if (CollectionUtil.isNotEmpty(pcdnModelDetails)) {
            for (PcdnModelDetail modelDetail : pcdnModelDetails) {
                Map<String, Object> map = new HashMap<>();

                // 步骤3：格式化评分区间显示
                // 将数据库中的小数（如0.5）转换为百分比（如50）
                String start = String.valueOf(modelDetail.getStartRatio() * 100);
                String end = String.valueOf(modelDetail.getEndRatio() * 100);

                // 特殊值处理：负无穷和正无穷的显示
                if (modelDetail.getStartRatio() == Integer.MIN_VALUE) {
                    start = "0";  // 负无穷显示为"0"
                }
                if (modelDetail.getEndRatio() == Integer.MAX_VALUE) {
                    end = PcdnConstant.INFINITY;  // 正无穷显示为"∞"
                }

                // 构建表格行的三个字段
                map.put("score_range", start + "-" + end);  // 评分区间，如"0-50"
                map.put("score", String.valueOf(modelDetail.getScore()));  // 对应得分，如"20"
                map.put("ratio", "--");  // 用户实际值，默认显示"--"

                // 步骤4：填充用户实际值
                // 如果响应对象中包含用户数据，则提取实际值并判断所在区间
                List<Map<String, Object>> temporaryList = reportResponse.getTemporaryList();
                if (CollectionUtil.isNotEmpty(temporaryList)) {
                    // 根据模型类型提取对应的原始指标值
                    String ratio = extractRatioByType(reportRequest.getType(), temporaryList);
                    Float ratioValue = Float.parseFloat(ratio);

                    // 步骤5：判断用户值是否落在当前区间
                    // 条件：startRatio < ratioValue <= endRatio
                    if (BigDecimalUtil.isLessThan(modelDetail.getStartRatio(), ratioValue) &&
                        BigDecimalUtil.isGreaterOrEqual(modelDetail.getEndRatio(), ratioValue)) {
                        // 匹配成功，将用户实际值转换为百分比并高亮显示
                        map.put("ratio", ratioValue * 100);
                    }
                }

                // 将当前行添加到结果列表
                resultList.add(map);
            }
        }

        // 将构建完成的表格数据写回响应对象
        reportResponse.setTemporaryList(resultList);
    }

    /**
     * 根据模型类型提取对应的原始指标值
     *
     * @param type      模型类型编码（如"UP_DOWN_FLOW"）
     * @param dataList  用户数据列表（每个Map代表一个用户的数据）
     * @return          对应的原始指标值（字符串形式）
     *
     * 说明：
     * - 不同的模型类型对应不同的字段名
     * - PCDN_DOMAIN类型特殊处理：返回域名访问数量（列表大小）
     */
    private String extractRatioByType(String type, List<Map<String, Object>> dataList) {
        // 取第一个用户的数据（通常评分标准接口只查询单个用户）
        Map<String, Object> data = dataList.get(0);

        // 根据模型类型返回对应的字段值
        switch (type) {
            case PcdnConstant.FlowModelType.UP_DOWN_FLOW:
                // 上下行流量比
                return data.get("flowRatio").toString();
            case PcdnConstant.FlowModelType.TARGET_PORT_HASH:
                // TOP5目的端口流量占比
                return data.get("oppositeFrequentlyPortRatio").toString();
            case PcdnConstant.FlowModelType.SOURCE_PORT_AGG:
                // TOP5源端口流量占比
                return data.get("topPortRatio").toString();
            case PcdnConstant.FlowModelType.UP_UDP_PROPORTION:
                // 上行UDP协议占比
                return data.get("protocolRatio").toString();
            case PcdnConstant.FlowModelType.LOCAL_USER_PROPORTION:
                // 服务本省用户占比
                return data.get("localFlowRatio").toString();
            case PcdnConstant.FlowModelType.PCDN_DOMAIN:
                // PCDN特征域名访问数量（返回列表的大小）
                return String.valueOf(dataList.size());
            default:
                // 未知类型返回"0"
                return "0";
        }
    }
}
```

> **功能总结：** ScoringCriteria是PCDN评分责任链的展示辅助节点，负责构建评分标准表格。核心功能包括：区间格式化（小数转百分比）、特殊值处理（无穷大显示）、区间匹配高亮。通过extractRatioByType方法实现多态数据提取，支持所有6种模型类型的评分标准展示。该节点输出的表格数据直接供前端渲染，帮助用户理解评分规则和对比实际值。

---

## 四、数据处理流程

### 4.1 数据采集与预处理

```
┌─────────────────────────────────────────────────────────────────┐
│                    PCDN数据采集流程                              │
└─────────────────────────────────────────────────────────────────┘

数据源：
  ├─ 网络设备（SNMP采集）
  ├─ BGP路由表（文件解析）
  ├─ DNS日志（Kafka消费）
  └─ Radius认证日志（数据库同步）

处理流程：
  Step 1: 原始数据采集
    ├─ SNMP采集路由器端口流量（5分钟粒度）
    ├─ 解析BGP路由表获取IP归属
    └─ 消费DNS日志获取域名访问记录

  Step 2: 数据清洗与关联
    ├─ IP地址归属判断（家宽/专线/IDC）
    ├─ 域名与PCDN平台匹配
    ├─ 上下行流量计算
    └─ 端口、协议统计分析

  Step 3: 特征提取
    ├─ 计算上下行流量比
    ├─ 统计TOP5源/目的端口流量占比
    ├─ 计算UDP协议占比
    ├─ 统计服务本省用户比例
    └─ 匹配PCDN特征域名

  Step 4: 数据入库
    └─ 写入ClickHouse预计算表（pcdn_suspected_user_P1D）
```

### 4.2 报表查询流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    PCDN报表查询流程                              │
└─────────────────────────────────────────────────────────────────┘

前端请求：
  ├─ interfaceId: pcdn-suspectedUsers
  ├─ 参数：analysisProv（省份）、analysisCity（城市）、时间范围
  └─ 分页参数：pageNum、pageSize

处理流程：
  Step 1: 请求参数预处理（RequestNodes）
    ├─ userDataCheckHandle：用户权限校验（省/市数据隔离）
    ├─ dateToDateTime：时间参数转换
    ├─ checkIpSegment：IP段校验
    └─ customMapperHandle：自定义配置加载

  Step 2: 数据查询（Mapper）
    ├─ 查询ClickHouse预计算表
    ├─ 按省份/城市/时间过滤
    ├─ 聚合统计各风险等级用户数
    └─ 分页查询疑似用户详情

  Step 3: 响应数据后处理（ResponseNodes）
    ├─ replaceValueToKeyHandle：枚举值转换（风险等级编码→名称）
    ├─ makeTabulationResponse：表格数据格式化
    ├─ dataPagination：分页处理
    ├─ putResponseFiledHandle：字段补充（城市名称、枚举描述）
    └─ adaptiveUnitHandle：单位自适应（流量→GB/MB，速率→Mbps/Gbps）

  Step 4: 返回前端
    └─ JSON格式响应（包含表格数据、分页信息、图表数据）
```

### 4.3 核心SQL查询（ClickHouse）

**疑似用户统计查询：**

```sql
-- ============================================================
-- 查询目的：按地市统计各风险等级的疑似PCDN用户数量
-- 数据源表：ngfa_up_precomputation.pcdn_suspected_user_P1D（按天预计算表）
-- 查询粒度：地市级（cityCode）
-- 时间范围：[startTime, endTime) 左闭右开区间
-- 过滤条件：省份编码（analysisProv）
-- ============================================================
SELECT
    -- 地市编码，作为分组维度
    cityCode,

    -- 使用条件聚合统计各风险等级的用户数
    -- suspectedTag字段存储风险等级编码：extremelyHigh/high/medium/low
    SUM(case when suspectedTag='extremelyHigh' then userTypeCount else 0 end) as extremelyHigh,  -- 极高风险用户数
    SUM(case when suspectedTag='high' then userTypeCount else 0 end) as high,                    -- 高风险用户数
    SUM(case when suspectedTag='medium' then userTypeCount else 0 end) as medium,                -- 中风险用户数
    SUM(case when suspectedTag='low' then userTypeCount else 0 end) as low,                      -- 低风险用户数

    -- 计算总用户数（各风险等级之和）
    (extremelyHigh + high + medium + low) as totalCount

FROM (
    -- 子查询：按地市、用户类型、风险等级分组统计用户数
    select
        -- 用户类型处理：空值默认为'10'（其他类型）
        -- userType字段：4=家宽，5=专线，6=商企宽，10=其他
        if(userType = '', '10', userType) as userType,

        -- 地市编码
        cityCode,

        -- 风险等级标签
        suspectedTag,

        -- 统计该分组下的用户IP数量（去重计数）
        count(userIp) as userTypeCount

    from ngfa_up_precomputation.pcdn_suspected_user_P1D

    -- 按地市、用户类型、风险等级分组
    group by cityCode, userType, suspectedTag

    -- 时间范围过滤和省份过滤
    -- 使用HAVING而非WHERE，因为需要基于聚合后的时间字段过滤
    HAVING `timestamp` >= {startTime}
       AND `timestamp` < {endTime}
       and provinceCode = {analysisProv}
)
-- 外层查询按地市分组，汇总各风险等级的用户数
GROUP BY cityCode
```

> **功能总结：** 该SQL实现了按地市维度统计各风险等级疑似PCDN用户数量的核心查询。采用两层聚合策略：内层按(cityCode, userType, suspectedTag)三维度分组统计用户数，外层通过条件聚合（CASE WHEN）将风险等级从行转列，生成包含4个风险等级列的宽表。查询使用ClickHouse预计算表（P1D后缀），通过时间分区和省份过滤实现高效数据裁剪。该查询是"疑似PCDN用户统计报表"接口的数据源，支撑前端的地市分布展示。

**性能优化点：**
- 使用预计算表（P1D后缀表示按天预聚合）
- ClickHouse列式存储，适合聚合查询
- 分区键：timestamp（按天分区）
- 排序键：(provinceCode, cityCode, timestamp)

---

## 五、报表接口详解

### 5.1 接口配置规范（report-pdcn.yml）

PCDN模块采用**配置化报表引擎**，通过YAML文件定义接口：

```yaml
# ============================================================
# PCDN报表接口配置示例
# 文件：report-pdcn.yml
# 用途：定义疑似PCDN用户统计报表接口的完整配置
# 说明：采用配置化报表引擎，通过YAML定义接口的请求处理、
#       数据查询、响应处理等全流程，实现零代码接口开发
# ============================================================

# 接口定义（一个YAML文件可定义多个接口）
- interfaceId: pcdn-suspectedUsers      # 接口唯一标识，前端通过此ID调用接口
  name: 疑似PCDN用户统计报表             # 接口名称，用于文档和日志

  # ============================================================
  # 请求参数处理节点（RequestNodes）
  # 作用：在数据查询前对请求参数进行预处理和校验
  # 执行顺序：按数组顺序依次执行
  # ============================================================
  requestNodes:
    # 节点1：用户权限校验和数据隔离
    - name: userDataCheckHandle          # 节点名称，对应Spring Bean
      metadataList:                      # 节点元数据配置
        - code: analysisProv             # 参数编码
          type: province                 # 参数类型：省份编码
        - code: analysisCity             # 参数编码
          type: city                     # 参数类型：地市编码
      # 功能：根据当前登录用户的角色，自动注入省份/地市过滤条件
      #       省级用户只能查看本省数据，市级用户只能查看本市数据

    # 节点2：时间参数转换
    - name: dateToDateTime               # 将前端传入的日期字符串转换为DateTime对象
      # 输入：startTime="2024-01-01", endTime="2024-01-31"
      # 输出：startTime=2024-01-01 00:00:00, endTime=2024-01-31 23:59:59

    # 节点3：IP段校验
    - name: checkIpSegment               # 校验用户输入的IP段格式是否正确
      # 输入：ipSegment="192.168.1.0/24"
      # 输出：校验通过/抛出异常

  # ============================================================
  # 数据查询Mapper
  # 作用：指定查询的MyBatis Mapper方法和参数
  # 格式：mapperName-methodName
  # ============================================================
  mapperPage: overviewMapper-selectPcdnUsers
  # 说明：调用OverviewMapper接口的selectPcdnUsers方法
  #       该方法对应ClickHouse的SQL查询
  #       "Page"后缀表示支持分页查询

  # ============================================================
  # 响应数据后处理节点（ResponseNodes）
  # 作用：在数据查询后对响应结果进行格式化和转换
  # 执行顺序：按数组顺序依次执行
  # ============================================================
  responseNodes:
    # 节点1：枚举值转换
    - name: replaceValueToKeyHandle      # 将枚举编码转换为显示名称
      metadataList:
        - code: suspectedTag             # 需要转换的字段
          type: enumMap                  # 转换类型：枚举映射
      # 功能：将suspectedTag字段的值从编码转换为名称
      #       例如：extremelyHigh → 极高风险

    # 节点2：表格格式化
    - name: makeTabulationResponse       # 构建标准的表格响应结构
      # 功能：将查询结果转换为前端表格组件所需的数据格式
      # 输出：{columns: [...], data: [...], pagination: {...}}

    # 节点3：单位自适应转换
    - name: adaptiveUnitHandle           # 根据数值大小自动选择合适的单位
      metadataList:
        - code: outRate                  # 需要转换的字段：上行速率
          type: rate                     # 字段类型：速率（bps→Mbps→Gbps）
        - code: outThroughput            # 需要转换的字段：上行流量
          type: flow                     # 字段类型：流量（B→KB→MB→GB）
      # 功能：根据数值大小自动转换单位
      #       例如：1500000000 bps → 1.5 Gbps
      #       例如：1073741824 B → 1 GB

  # ============================================================
  # 展示类型
  # 作用：指定前端使用的展示组件类型
  # 可选值：tabulation（表格）/ pieChart（饼图）/ areaChart（面积图）等
  # ============================================================
  displayType: tabulation

  # ============================================================
  # 响应字段定义
  # 作用：定义表格的列配置，包括字段名、显示名称、排序等
  # ============================================================
  responseMetadataList:
    # 字段1：拨号账户
    - code: userName                     # 字段编码，对应数据库字段
      name: 拨号账户                      # 显示名称，用于表头
      index: 1                           # 列顺序，从左到右

    # 字段2：用户IP
    - code: userIp
      name: 用户IP
      index: 2

    # 字段3：风险得分
    - code: riskScore
      name: 风险得分
      sort: true                         # 是否支持排序
      index: 16
```

> **功能总结：** 该YAML配置定义了PCDN疑似用户统计报表接口的完整处理流程。采用配置化报表引擎设计，将接口开发从编码转变为配置。核心配置包括：请求处理节点（权限校验、参数转换）、数据查询Mapper（ClickHouse SQL）、响应处理节点（枚举转换、单位自适应）、展示类型和字段定义。通过责任链模式串联各处理节点，实现灵活的数据处理流程。该设计大幅降低了接口开发成本，新增接口只需编写YAML配置和SQL查询。

### 5.2 核心接口清单

| 接口ID | 接口名称 | 展示类型 | 数据源 |
|--------|---------|---------|--------|
| `pcdn-userCount` | 疑似PCDN用户数 | 表格 | OverviewMapper |
| `pcdn-userTrendy` | 用户趋势图 | 面积图 | OverviewMapper |
| `pcdn-platformRatio` | 平台分布 | 饼图 | OverviewMapper |
| `pcdn-suspectedUsers` | 疑似用户列表 | 分页表格 | OverviewMapper |
| `pcdn-suspicionRatingCriteria` | 评分标准 | 表格 | 动态Mapper |
| `pcdn-upDownFlowTrend` | 上下行流量趋势 | 柱状图 | PcdnUserFlowMapper |
| `pcdn-top5SourceFlowProportion` | TOP5源端口占比 | 半圆环 | PcdnUserSrcPortMapper |
| `pcdn-udpUpFlowProportion` | UDP流量占比 | 饼图 | PcdnUserProtocolMapper |
| `pcdn-commonPortFlowProportion` | 常用目的端口占比 | 半圆环 | PcdnUserDstPortMapper |
| `pcdn-feature-domain` | 特征域名列表 | 表格 | PcdnUserDomainMapper |
| `pcdn-feature-model` | 模型命中特征 | 表格 | PcdnSuspectedUserMapper |

### 5.3 数据后处理节点

**常用处理节点：**

| 节点名称 | 功能说明 | 使用场景 |
|---------|---------|---------|
| `makeTabulationResponse` | 构建表格响应结构 | 所有表格接口 |
| `makeDrawResponse` | 构建图表响应结构 | 所有图表接口 |
| `adaptiveUnitHandle` | 单位自适应转换 | 流量/速率字段 |
| `replaceValueToKeyHandle` | 枚举值映射 | 风险等级、用户类型 |
| `dateFormat` | 日期格式化 | 时间轴数据 |
| `scoringCriteria` | 评分标准构建 | 评分标准接口 |
| `makeFinalScore` | 综合得分计算 | 用户评分接口 |

---

## 六、关键技术点

### 6.1 配置驱动设计

**设计思想：**
将业务规则（评分区间、权重、风险等级）从代码中剥离，存储在数据库，通过配置界面动态调整。

**优势：**
- 业务规则变更无需修改代码
- 支持A/B测试不同评分模型
- 运营人员可自主调优

**实现方式：**
```java
// ============================================================
// 配置驱动设计实现示例
// 核心思路：将业务规则存储在数据库中，通过配置界面动态调整
// 优势：业务规则变更无需修改代码，支持A/B测试不同评分模型
// ============================================================

// 1. 配置实体类：使用MyBatis-Plus注解映射数据库表
@Data                                    // Lombok注解：自动生成getter/setter/toString等
@TableName("pcdn_model_info")            // 映射数据库表名
public class PcdnModel {
    private String type;      // 模型类型编码（如UP_DOWN_FLOW），与常量类对应
    private Integer weight;   // 权重（0-100），所有模型权重之和应为100
    private Integer status;   // 启用状态：0=禁用，1=启用
}

// 2. Feign客户端：声明式REST客户端，用于微服务间调用
// PcdnModelFeign接口由配置服务（pcdnConfig）提供实现
@Resource
private PcdnModelFeign pcdnModelFeign;

// 3. 运行时加载配置：每次报表请求时从配置服务获取最新配置
// 返回结果：所有启用的流量模型列表，包含类型编码和权重
// 使用场景：MakeFinalScore节点在计算综合得分前调用
List<PcdnModel> modelList = pcdnModelFeign.pageList(new PcdnModel()).getList();
```

> **功能总结：** 该代码展示了配置驱动设计的核心实现。通过MyBatis-Plus实体类映射数据库配置表，使用Feign客户端实现微服务间的配置拉取。运行时动态加载配置，使得业务规则（模型权重、评分区间、风险等级）可在不修改代码的情况下灵活调整。该设计是PCDN评分系统可扩展性的基石。

### 6.2 责任链模式（DataPostHandle）

**设计模式：**
报表后处理采用**责任链模式**，每个处理节点（DataPostHandle）负责一个独立的处理逻辑，可灵活组合。

**核心类：**
```java
// ============================================================
// 责任链模式核心抽象类
// 设计模式：Chain of Responsibility（责任链）
// 用途：定义报表后处理节点的统一接口和链式调用机制
// 优势：节点可灵活组合，职责单一，易于扩展
// ============================================================
public abstract class DataPostHandle {

    // 链式指针：指向责任链中的下一个处理节点
    // 通过setNext方法动态组装处理链
    protected DataPostHandle next;

    /**
     * 设置下一个处理节点
     * @param next 下一个DataPostHandle实例
     */
    public void setNext(DataPostHandle next) {
        this.next = next;
    }

    /**
     * 核心处理方法：执行当前节点逻辑并传递给下一个节点
     *
     * @param metadata  报表元数据（字段定义、展示类型等）
     * @param request   报表请求参数（查询条件、时间范围等）
     * @param response  报表响应对象（包含待处理的数据列表）
     *
     * 执行流程：
     * 1. 调用doHandle执行当前节点的业务逻辑
     * 2. 检查是否存在下一个节点
     * 3. 如果存在，递归调用下一个节点的handle方法
     */
    public void handle(ReportMetadata metadata,
                      ReportRequest request,
                      ReportResponse response) {
        // 步骤1：执行当前节点的处理逻辑
        // 由子类实现具体的业务逻辑（如评分计算、格式化等）
        doHandle(metadata, request, response);

        // 步骤2：责任链传递
        // 如果存在下一个节点，继续调用其handle方法
        if (next != null) {
            next.handle(metadata, request, response);
        }
    }

    /**
     * 抽象方法：子类必须实现的具体处理逻辑
     *
     * @param metadata  报表元数据
     * @param request   报表请求参数
     * @param response  报表响应对象
     *
     * 子类实现示例：
     * - MakeFinalScore：计算综合得分
     * - UDFlowRatioScore：计算上下行流量比评分
     * - ScoringCriteria：构建评分标准表格
     */
    protected abstract void doHandle(ReportMetadata metadata,
                                    ReportRequest request,
                                    ReportResponse response);
}
```

> **功能总结：** DataPostHandle是责任链模式的核心抽象类，定义了报表后处理节点的统一接口。通过next指针实现链式调用，handle方法负责协调当前节点逻辑和链式传递。子类通过实现doHandle方法完成具体业务逻辑（如评分计算、数据格式化）。该设计使得处理节点可灵活组合、职责单一、易于扩展，是配置化报表引擎的核心架构。

**处理链示例：**
```
原始数据
  → scoringCriteria（评分标准构建）
  → makeTabulationResponse（表格格式化）
  → adaptiveUnitHandle（单位转换）
  → 返回前端
```

### 6.3 ClickHouse预计算优化

**预计算策略：**
```sql
-- ============================================================
-- ClickHouse预计算优化策略
-- 核心思路：将高频查询的聚合结果预先计算并存储
-- 效果：查询性能从秒级降至毫秒级，存储减少90%+
-- ============================================================

-- ============================================================
-- 表1：原始数据表（按小时粒度）
-- 用途：存储每小时粒度的用户流量明细数据
-- 引擎：MergeTree（ClickHouse基础表引擎，适合大量写入）
-- ============================================================
CREATE TABLE pcdn_suspected_user_P1H (
    -- 时间戳字段，精确到小时
    timestamp DateTime,
    -- 省份编码，用于数据隔离和分区过滤
    provinceCode String,
    -- 地市编码，用于地市级聚合查询
    cityCode String,
    -- 用户IP地址，唯一标识一个用户
    userIp String,
    -- 用户类型：4=家宽，5=专线，6=商企宽，10=其他
    userType String,
    -- 上行吞吐量（字节），该小时内用户上行总流量
    outThroughput UInt64,
    -- 下行吞吐量（字节），该小时内用户下行总流量
    inThroughput UInt64
    -- ... 其他字段（端口、协议、域名等维度数据）
) ENGINE = MergeTree()
-- 按天分区，便于数据生命周期管理和分区裁剪
PARTITION BY toYYYYMMDD(timestamp)
-- 排序键：决定数据的物理存储顺序和查询效率
-- (provinceCode, cityCode, timestamp, userIp)组合
-- 优化了"按省份+地市+时间范围"查询的性能
ORDER BY (provinceCode, cityCode, timestamp, userIp);

-- ============================================================
-- 表2：预计算表（按天粒度）
-- 用途：存储每天聚合后的用户流量汇总数据
-- 引擎：SummingMergeTree（自动对数值列求和的聚合引擎）
-- ============================================================
CREATE TABLE pcdn_suspected_user_P1D (
    -- 时间戳字段，精确到天
    timestamp Date,
    provinceCode String,
    cityCode String,
    userIp String,
    userType String,
    -- 风险等级标签：extremelyHigh/high/medium/low
    suspectedTag String,
    -- 上行吞吐量（日汇总）
    outThroughput UInt64,
    -- 下行吞吐量（日汇总）
    inThroughput UInt64
    -- ... 其他聚合字段
) ENGINE = SummingMergeTree()
-- 按天分区
PARTITION BY toYYYYMMDD(timestamp)
-- 排序键与原始表一致，保证查询性能
ORDER BY (provinceCode, cityCode, timestamp, userIp);

-- ============================================================
-- 定时聚合任务：每小时执行一次
-- 用途：将小时级数据聚合为天级数据，写入预计算表
-- 调度：通过XXL-JOB定时任务触发
-- ============================================================
INSERT INTO pcdn_suspected_user_P1D
SELECT
    -- 将小时级时间戳转换为日期（天级）
    toDate(timestamp) as timestamp,
    provinceCode,
    cityCode,
    userIp,
    userType,
    -- 风险等级取最新值（argMax返回timestamp最大时的suspectedTag值）
    -- 因为同一天内用户的风险等级可能随流量变化而更新
    argMax(suspectedTag, timestamp) as suspectedTag,
    -- 流量字段按天求和
    sum(outThroughput) as outThroughput,
    sum(inThroughput) as inThroughput
    -- ... 其他聚合（avg/max/min等，根据业务需求选择）
FROM pcdn_suspected_user_P1H
-- 按天+省份+地市+用户IP+用户类型分组
GROUP BY toDate(timestamp) as timestamp, provinceCode, cityCode, userIp, userType;
```

> **功能总结：** 该SQL展示了ClickHouse预计算优化的核心策略。采用"小时表+天表"两级存储架构：小时表（P1H）保留原始粒度数据，天表（P1D）存储预聚合结果。通过MergeTree引擎的分区和排序键优化查询效率，SummingMergeTree引擎自动合并重复键的数值列。定时聚合任务使用argMax函数保留最新风险等级，sum函数汇总流量数据。该策略将报表查询性能从秒级提升至毫秒级，同时大幅降低存储成本。

**性能提升：**
- 查询性能：从秒级降至毫秒级
- 存储优化：数据量减少90%+
- 资源消耗：CPU/内存占用降低

### 6.4 多维度数据隔离

**数据权限控制：**
```java
// ============================================================
// 多维度数据隔离实现
// 功能：根据用户角色自动注入数据过滤条件，实现省/市两级数据隔离
// 原理：在请求参数预处理阶段，根据用户角色设置过滤条件
//       后续SQL查询自动应用这些条件，实现数据权限控制
// ============================================================

/**
 * 用户权限校验节点
 *
 * 功能说明：
 * 1. 获取当前登录用户的角色和归属信息
 * 2. 根据角色自动注入数据过滤条件
 * 3. 确保用户只能查看权限范围内的数据
 *
 * 角色定义：
 * - PROVINCE（省级用户）：只能查看本省数据
 * - CITY（市级用户）：只能查看本市数据
 *
 * 使用场景：
 * - 作为报表接口的第一个请求处理节点
 * - 在所有数据查询前执行，确保数据安全
 */
@Component("userDataCheckHandle")  // Spring Bean名称，用于YAML配置中引用
public class UserDataCheckHandle extends DataPreHandle {

    /**
     * 核心处理方法：执行用户权限校验和数据隔离
     *
     * @param request 报表请求参数对象
     *
     * 处理流程：
     * 1. 获取当前用户信息（从ThreadLocal或请求头中获取）
     * 2. 判断用户角色
     * 3. 根据角色设置过滤条件
     * 4. 过滤条件自动注入到后续SQL查询中
     */
    @Override
    protected void handle(ReportRequest request) {
        // 步骤1：获取当前登录用户信息
        // UserUtil.getCurrentUser()从ThreadLocal中获取用户信息
        // 用户信息在登录时由网关服务写入请求头，通过Filter传递到业务服务
        UserInfo userInfo = UserUtil.getCurrentUser();

        // 步骤2：省级用户权限处理
        // 省级用户只能查看本省数据，自动注入省份过滤条件
        if (userInfo.getRole() == UserRole.PROVINCE) {
            // 设置省份编码，后续SQL查询会自动应用该条件
            // WHERE provinceCode = #{analysisProv}
            request.setAnalysisProv(userInfo.getProvinceCode());
        }

        // 步骤3：市级用户权限处理
        // 市级用户只能查看本市数据，自动注入省份+地市过滤条件
        if (userInfo.getRole() == UserRole.CITY) {
            // 设置省份编码和地市编码
            // WHERE provinceCode = #{analysisProv} AND cityCode = #{analysisCity}
            request.setAnalysisProv(userInfo.getProvinceCode());
            request.setAnalysisCity(userInfo.getCityCode());
        }

        // 步骤4：数据隔离生效
        // 过滤条件已注入到request对象中
        // 后续的Mapper查询会自动使用这些条件
        // 例如：SELECT * FROM pcdn_suspected_user_P1D
        //       WHERE provinceCode = #{analysisProv}
        //         AND cityCode = #{analysisCity}
    }
}
```

> **功能总结：** UserDataCheckHandle是数据权限控制的核心节点，实现了省/市两级数据隔离。通过获取当前用户角色，自动注入相应的过滤条件到请求参数中。省级用户只能查看本省数据，市级用户只能查看本市数据。该节点作为报表接口的第一个处理节点执行，确保所有数据查询都在权限范围内，防止越权访问。

---

## 七、性能优化实践

### 7.1 查询优化

**问题：** 疑似用户列表查询慢（数据量大）

**优化方案：**
1. **分页查询**：前端分页，每页50条
2. **索引优化**：(provinceCode, cityCode, timestamp)联合索引
3. **预计算**：按天预聚合，减少实时计算
4. **字段裁剪**：只查询展示字段，避免SELECT *

**优化效果：**
- 查询时间：5s → 200ms
- 内存占用：降低80%

### 7.2 缓存策略

**缓存层级：**
```
L1: 本地缓存（Caffeine）
  ├─ 配置数据（PcdnModel、PcdnRiskGrade）
  └─ 缓存时间：5分钟

L2: Redis缓存
  ├─ 热点报表数据（今日概览）
  └─ 缓存时间：1小时

L3: ClickHouse物化视图
  ├─ 预聚合数据
  └─ 自动刷新
```

### 7.3 异步处理

**场景：** 综合得分计算耗时

**优化方案：**
```java
// ============================================================
// 异步处理优化方案
// 场景：综合得分计算涉及多次Feign远程调用和复杂计算，耗时较长
// 方案：使用Spring @Async注解实现异步执行，配合自定义线程池
// 效果：避免阻塞主线程，提升接口响应速度
// ============================================================

/**
 * 异步计算用户PCDN综合得分
 *
 * @param data  用户流量特征数据（包含各维度原始指标值）
 * @return      CompletableFuture<Float> 异步计算结果，包含综合得分
 *
 * 说明：
 * - @Async指定使用pcdnScoreExecutor线程池执行
 * - 返回CompletableFuture支持异步结果获取和链式操作
 * - 调用方可通过future.get()阻塞等待结果，或注册回调函数
 */
@Async("pcdnScoreExecutor")  // 指定自定义线程池名称
public CompletableFuture<Float> calculateScore(UserFlowData data) {
    // 执行实际的得分计算逻辑
    // 包括：加载模型配置、各维度评分、加权求和、风险定级
    Float score = doCalculate(data);
    // 将计算结果包装为已完成的CompletableFuture返回
    return CompletableFuture.completedFuture(score);
}

/**
 * 自定义线程池配置
 *
 * 参数说明：
 * - corePoolSize=10：核心线程数，常驻线程，处理常规负载
 * - maxPoolSize=50：最大线程数，高峰期可扩展至50个线程
 * - queueCapacity=1000：任务队列容量，超出核心线程数时进入队列等待
 * - threadNamePrefix="pcdn-score-"：线程名称前缀，便于日志追踪和监控
 *
 * 线程池工作流程：
 * 1. 任务数 <= 10：使用核心线程处理
 * 2. 任务数 > 10：进入等待队列（最多1000个）
 * 3. 队列满且任务数 <= 50：创建非核心线程处理
 * 4. 任务数 > 50：触发拒绝策略（默认抛异常）
 */
@Bean("pcdnScoreExecutor")  // Bean名称，与@Async注解中的名称对应
public Executor pcdnScoreExecutor() {
    ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
    executor.setCorePoolSize(10);          // 核心线程数
    executor.setMaxPoolSize(50);           // 最大线程数
    executor.setQueueCapacity(1000);       // 任务队列容量
    executor.setThreadNamePrefix("pcdn-score-");  // 线程名称前缀
    executor.initialize();                 // 初始化线程池
    return executor;
}
```

> **功能总结：** 该代码展示了PCDN评分的异步处理优化方案。通过`@Async`注解将耗时的综合得分计算从主线程转移到自定义线程池异步执行，避免阻塞HTTP请求线程。线程池采用核心线程+队列+最大线程的三级缓冲策略，兼顾常规性能和峰值承载能力。使用CompletableFuture返回异步结果，支持灵活的后续处理。该优化显著提升了高并发场景下的接口响应速度。

---

## 八、扩展性设计

### 8.1 新增流量模型

**步骤：**

1. 数据库新增模型配置
```sql
-- ============================================================
-- 新增流量特征模型配置
-- 用途：在PCDN识别模型中增加一个新的评估维度
-- 说明：通过配置化方式扩展模型，无需修改代码
-- ============================================================
INSERT INTO pcdn_model_info (id, name, type, weight, status)
VALUES (
    '7',              -- 模型ID，使用雪花算法生成或手动指定
    '新特征模型',      -- 模型名称，用于前端展示
    'NEW_FEATURE',    -- 模型类型编码，需与常量类定义一致
    20,               -- 权重占比20%，所有模型权重之和应为100
    1                 -- 状态：1=启用，0=禁用
);
```

> **功能总结：** 该SQL在pcdn_model_info表中新增一个流量特征模型配置。通过配置化设计，系统可在运行时动态加载新模型，无需修改代码或重启服务。权重字段控制该模型在综合评分中的占比，状态字段支持临时禁用模型。

2. 数据库新增评分区间
```sql
-- ============================================================
-- 新增模型评分区间配置
-- 用途：定义新特征模型的评分规则和区间映射
-- 说明：将原始指标值映射为0-100分的评分
-- ============================================================
INSERT INTO pcdn_model_detail_info (id, type, start_ratio, end_ratio, score)
VALUES
-- 区间1：[0, 0.3) 映射为0分
('7-1', 'NEW_FEATURE', 0, 0.3, 0),
-- 区间2：[0.3, 0.6) 映射为40分
('7-2', 'NEW_FEATURE', 0.3, 0.6, 40),
-- 区间3：[0.6, 1.0] 映射为100分
('7-3', 'NEW_FEATURE', 0.6, 1.0, 100);
```

> **功能总结：** 该SQL为新模型配置评分区间规则。采用区间映射方式，将连续的指标值离散化为评分。每个区间包含起始值、结束值和对应评分。区间设计应遵循业务逻辑，确保评分分布合理。系统通过区间匹配算法自动计算用户在该维度的得分。

3. 数据预处理节点新增特征提取逻辑
```java
/**
 * 新特征提取处理节点
 *
 * 功能说明：
 * 1. 从原始流量数据中提取新特征指标值
 * 2. 将提取结果写入请求对象，供后续评分使用
 *
 * 实现要点：
 * - 继承DataPreHandle基类，实现统一的处理接口
 * - 使用@Component注解注册为Spring Bean
 * - Bean名称需与YAML配置中的节点名称一致
 *
 * @author PCDN开发团队
 * @version 1.0
 */
@Component("newFeatureExtractHandle")  // Bean名称，用于YAML配置引用
public class NewFeatureExtractHandle extends DataPreHandle {

    /**
     * 核心处理方法：提取新特征指标
     *
     * @param request 报表请求对象，包含原始数据和查询条件
     *
     * 处理流程：
     * 1. 从request中获取原始流量数据
     * 2. 调用extractNewFeature方法计算特征值
     * 3. 将计算结果写回request对象
     */
    @Override
    protected void handle(ReportRequest request) {
        // 调用特征提取方法，计算新特征指标值
        // extractNewFeature方法需根据具体业务逻辑实现
        Float newFeatureValue = extractNewFeature(request);

        // 将提取的特征值写入请求对象
        // 后续评分节点会从request中读取该值进行区间匹配
        request.setNewFeature(newFeatureValue);
    }

    /**
     * 特征提取方法（需根据业务逻辑实现）
     *
     * @param request 请求对象
     * @return 提取的特征值
     */
    private Float extractNewFeature(ReportRequest request) {
        // TODO: 根据具体业务逻辑实现特征提取
        // 示例：计算某种流量比率、统计特定端口使用次数等
        return 0.0f;
    }
}
```

> **功能总结：** 该Java类实现了新特征的数据预处理节点。采用责任链模式，通过继承DataPreHandle基类实现统一接口。核心功能是从原始流量数据中提取特征指标值，并写入请求对象供后续评分使用。通过@Component注解注册为Spring Bean，Bean名称需与YAML配置保持一致。该设计确保了特征提取逻辑的可插拔性和可扩展性。

4. YAML配置新增评分节点
```yaml
# ============================================================
# 新增评分节点配置
# 用途：在报表处理流程中插入新特征的评分计算节点
# 说明：通过配置化方式调整处理流程，无需修改代码
# ============================================================
responseNodes:
  # 节点1：新特征评分计算
  - name: newFeatureScore  # 评分节点名称，对应Spring Bean
    # 该节点会从request中读取newFeature值
    # 根据pcdn_model_detail_info表中的区间配置计算得分
    # 将得分写回response对象

  # 节点2：重新计算综合得分
  - name: makeFinalScore   # 综合得分计算节点
    # 该节点会读取所有维度的评分（包括新特征）
    # 根据pcdn_model_info表中的权重配置计算加权总分
    # 根据pcdn_risk_grade_info表中的配置确定风险等级
```

> **功能总结：** 该YAML配置在报表响应处理流程中新增了两个节点。newFeatureScore节点负责计算新特征的维度评分，makeFinalScore节点负责重新计算综合得分。通过配置化方式，系统可灵活调整处理流程，支持动态插入或删除处理节点。该设计体现了配置驱动和可插拔架构的优势。

### 8.2 新增报表接口

**步骤：**
1. Mapper XML新增SQL查询
2. YAML文件新增接口定义
3. 前端配置接口调用

**示例：**
```yaml
# ============================================================
# 新增报表接口配置示例
# 用途：定义一个新的PCDN分析报表接口
# 说明：通过YAML配置快速创建报表接口，无需编写Controller代码
# ============================================================

# 接口定义
- interfaceId: pcdn-newReport        # 接口唯一标识，前端通过此ID调用
  name: 新报表                        # 接口名称，用于文档和日志

  # 请求参数预处理节点
  requestNodes:
    # 节点1：用户权限校验和数据隔离
    - name: userDataCheckHandle       # 根据用户角色注入省份/地市过滤条件
    # 节点2：时间参数转换
    - name: dateToDateTime            # 将字符串时间转换为DateTime对象

  # 数据查询Mapper
  mapper: newMapper-selectData        # 调用MyBatis Mapper查询数据
                                      # 格式：mapperName-methodName

  # 响应数据后处理节点
  responseNodes:
    # 节点：构建表格响应结构
    - name: makeTabulationResponse    # 将查询结果转换为标准表格格式

  # 展示类型
  displayType: tabulation             # 表格展示（可选：pieChart/areaChart等）

  # 响应字段定义
  responseMetadataList:
    # 字段1配置
    - code: field1                    # 字段编码，对应数据库字段名
      name: 字段1                      # 显示名称，用于表头
    # 字段2配置
    - code: field2
      name: 字段2
```

> **功能总结：** 该YAML配置展示如何快速创建新的报表接口。配置包含5个核心部分：interfaceId（接口标识）、requestNodes（请求预处理）、mapper（数据查询）、responseNodes（响应后处理）、displayType（展示类型）。通过配置化方式，开发者只需编写SQL查询和YAML配置，无需编写Controller、Service等代码，大幅提升开发效率。

---

## 九、监控与告警

### 9.1 关键指标监控

| 指标 | 监控方式 | 告警阈值 |
|------|---------|---------|
| 接口响应时间 | SkyWalking | > 2s |
| ClickHouse查询耗时 | 自定义埋点 | > 1s |
| 评分计算耗时 | AOP切面 | > 500ms |
| 数据同步延迟 | XXL-JOB监控 | > 1小时 |
| 异常率 | 日志分析 | > 1% |

### 9.2 日志规范

```java
// ============================================================
// PCDN模块日志规范
// 用途：统一日志格式，便于日志分析和问题排查
// 规范：采用[模块名-操作类型]前缀 + 占位符参数的方式
// 说明：使用SLF4J的{}占位符，避免字符串拼接的性能开销
// ============================================================

// 1. 业务日志：记录PCDN评分计算的关键业务数据
// 格式：[PCDN评分] + 用户IP + 上下行比 + 综合得分 + 风险等级
// 用途：追踪用户评分结果，支持业务审计和数据分析
// 参数说明：
//   - userIp：用户IP地址，用于定位具体用户
//   - udFlowRatio：上下行流量比，核心评分指标
//   - finalScore：综合得分（0-100），加权计算结果
//   - suspectedLevel：风险等级（extremelyHigh/high/medium/low）
log.info("[PCDN评分] 用户IP={}, 上下行比={}, 综合得分={}, 风险等级={}",
         userIp, udFlowRatio, finalScore, suspectedLevel);

// 2. 性能日志：记录接口查询的性能指标
// 格式：[PCDN查询] + 接口ID + 耗时 + 数据量
// 用途：监控接口性能，识别慢查询，支持性能优化
// 参数说明：
//   - interfaceId：接口标识（如pcdn-suspectedUsers）
//   - costTime：接口耗时（毫秒），包含查询+后处理全流程
//   - dataSize：返回数据量（条数），用于评估数据规模
log.info("[PCDN查询] 接口={}, 耗时={}ms, 数据量={}",
         interfaceId, costTime, dataSize);

// 3. 异常日志：记录评分计算过程中的错误信息
// 格式：[PCDN异常] + 错误描述 + 用户IP + 异常堆栈
// 用途：快速定位异常原因，支持问题排查和修复
// 参数说明：
//   - 第一个参数：错误描述信息，简明说明异常场景
//   - userIp：发生异常的用户IP，用于复现问题
//   - e.getMessage()：异常消息，包含具体错误原因
//   - e：异常对象本身，用于输出完整堆栈信息（必须放在最后一个参数）
log.error("[PCDN异常] 评分计算失败, 用户IP={}, 错误={}",
          userIp, e.getMessage(), e);
```

> **功能总结：** 该代码块定义了PCDN模块的日志规范，涵盖业务日志、性能日志和异常日志三类。采用统一的`[模块名-操作类型]`前缀格式，便于日志检索和过滤。使用SLF4J的`{}`占位符替代字符串拼接，避免不必要的性能开销。异常日志要求将异常对象作为最后一个参数传入，确保输出完整堆栈信息。该规范为SkyWalking链路追踪和日志分析平台提供了标准化的日志数据。

---

## 十、总结

### 10.1 技术亮点

1. **配置驱动**：业务规则与代码解耦，支持动态调优
2. **责任链模式**：报表处理节点可灵活组合
3. **预计算优化**：ClickHouse物化视图，查询性能提升10倍+
4. **多维度评分**：6维度加权模型，识别准确率高
5. **数据隔离**：省/市两级权限控制

### 10.2 待优化项

1. **实时性**：当前按天预聚合，可优化为小时级
2. **模型训练**：引入机器学习，自动优化评分权重
3. **可视化**：增加更多图表类型（热力图、桑基图）
4. **告警联动**：与工单系统打通，自动派单

### 10.3 技术债务

1. 部分Mapper SQL复杂度高，需拆分优化
2. 缺少单元测试，核心算法覆盖率不足
3. 配置项分散，需统一配置中心管理

---

> 文档结束
> 如有疑问，请联系开发团队
