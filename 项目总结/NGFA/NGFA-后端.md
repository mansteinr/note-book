# 群顶综合流量分析平台 - 项目架构与模块分析文档

> 文档版本：1.0
> 生成日期：2026-07-12
> 项目名称：ngfa-cloud-parent-ctcc

---

## 一、项目概述

### 1.1 项目简介

群顶综合流量分析平台（ngfa-cloud-parent）是一个基于 Spring Cloud Alibaba 微服务架构构建的企业级流量分析系统，主要面向运营商和 IDC 场景，提供大规模网络流量的采集、处理、分析和可视化能力。

### 1.2 技术栈总览

| 类别 | 技术选型 | 版本 |
|------|---------|------|
| JDK | OpenJDK | 17 |
| 基础框架 | Spring Boot | 3.0.13 |
| 微服务框架 | Spring Cloud | 2022.0.0 |
| 微服务框架 | Spring Cloud Alibaba | 2022.0.0.0 |
| 注册/配置中心 | Nacos | 2.2.3 |
| 分布式任务 | XXL-JOB | 2.4.0 |
| 数据库 | MariaDB / MySQL | - |
| 列式数据库 | ClickHouse | 0.2.4 |
| 消息队列 | Kafka | 3.0.11 |
| 搜索引擎 | Elasticsearch | 7.17.1 |
| ORM | MyBatis-Plus | 3.5.3.2 |
| Excel处理 | EasyExcel | 3.3.1 |
| 网络采集 | SNMP4J | 3.5.0 |
| 链路追踪 | SkyWalking | 9.2.0 |
| 配置加密 | Jasypt | 3.0.3 |

### 1.3 主要功能

**自服务系统：**
- 流量分析
- 关联数据
- 常用功能
- 场景分析

**运维系统：**
- 流量分析
- 配置数据
- 设备管理
- 数据服务

---

## 二、工程结构

### 2.1 顶层目录结构

```
ngfa-cloud-parent-ctcc/
├── ngfa-cloud-base/            # 基础工程：封装基础抽象类、工具类、常量
├── ngfa-cloud-framework/       # 技术组件：公共starter组件集合
├── ngfa-cloud-gateway/         # 网关服务：统一入口、认证鉴权
├── ngfa-cloud-service/         # 微服务：系统核心运行的微服务集合
├── ngfa-cloud-module/          # 业务模块：可插拔的数据分析和展示模块
├── pom.xml                     # 父POM，统一依赖版本管理
└── README.md                   # 项目说明
```

---

## 三、模块详细分析

### 3.1 ngfa-cloud-base（基础工程）

#### 3.1.1 模块定位
系统抽象基础工程，为所有上层模块提供公共基础设施。

#### 3.1.2 核心包结构

| 包名 | 功能说明 |
|------|---------|
| `config` | Feign配置、命令行配置 |
| `constant` | 业务常量定义（枚举、Kafka Topic等） |
| `domain` | 基础实体类（BaseEntity、ResponseData、UserInfo等） |
| `filter` | Servlet过滤器（用户信息过滤器） |
| `listener` | Excel导入监听器 |
| `util` | 工具类集合（30+个工具类） |

#### 3.1.3 关键实现

**核心工具类：**

| 工具类 | 功能 |
|--------|------|
| `IpRangeUtils` | IPv4/IPv6地址段展开，支持双栈IP范围遍历 |
| `IpWhitelistValidator` | IP白名单校验 |
| `EasyExcelUtil` | Excel文件导入导出封装 |
| `PushKafka` | Kafka消息推送封装 |
| `KafkaConsumerGroupOffsetChecker` | Kafka消费组偏移量检查 |
| `SftpClientUtil` | SFTP文件传输工具 |
| `HttpUtil` / `RestTemplateUtil` | HTTP请求工具 |
| `EncryptionUtil` | 加密工具 |
| `CsvUtil` | CSV文件处理 |
| `DateTimeUtil` / `DateUtils` | 日期时间处理 |
| `BigDecimalUtil` / `DecimalFormatUtil` | 数值精度处理 |
| `PageHelperUtil` | 分页工具 |
| `UserUtil` | 用户信息获取 |
| `SnowFlakeUtil` | 雪花算法ID生成 |

**核心常量：**

- `BusConstant`：业务常量，包含客户区域类型枚举（ALL/IDC/城域网）、通知类型常量（AS号/BGP/路由采样比等）、计算运算符枚举、宽带类型枚举
- `KafKaTopic`：Kafka主题定义
- `StateConstant`：状态常量
- `IspTypeEnum`：运营商类型枚举
- `BgpTypeEnum`：BGP类型枚举
- `IpTypeEnum`：IP类型枚举

**核心实体：**

- `BaseEntity`：基础实体，实现序列化接口
- `ResponseData`：统一响应封装
- `UserInfo`：用户信息实体
- `NoticeBigData`：大数据通知实体
- `CustomCell`：自定义Excel单元格

#### 3.1.4 关键算法

**IP地址段展开算法（IpRangeUtils）：**
```
输入：起始IP、结束IP
处理：
  1. 判断IP版本（IPv4/IPv6）
  2. IPv4：转换为整数，遍历范围
  3. IPv6：字节数组递增遍历
输出：IP地址列表
```

---

### 3.2 ngfa-cloud-framework（技术组件）

#### 3.2.1 模块定位
技术组件集合，每个子包代表一个可复用的公共组件，以Spring Boot Starter形式提供。

#### 3.2.2 组件清单

##### 3.2.2.1 ngfa-spring-boot-starter-auth（认证组件）

**功能：** 基于OAuth2的资源服务器认证

**核心类：**
- `SecurityConfig`：安全配置，基于WebFlux的响应式安全链
- `CustomReactiveOpaqueTokenIntrospector`：自定义Opaque Token内省器
- `SecurityFilter`：安全过滤器
- `AuthUtil`：认证工具类

**实现逻辑：**
```
请求 → Bearer Token提取 → Opaque Token内省 → IAM服务校验 → 认证/拒绝
```

**配置项：**
- `security.exclude.urls`：免认证URL
- `security.auth-url`：IAM服务地址
- `security.client-id` / `security.client-secret`：客户端凭证

##### 3.2.2.2 ngfa-spring-boot-starter-ip（IP处理组件）

**功能：** IP地址拆分合并核心算法

**核心类：**
- `IPHandle`：IP拆分合并主处理器
- `IpAddressUtil`：IP地址工具
- `IpSplitOrMergeUtil`：IP拆分合并工具
- `IpUtil`：IP通用工具

**核心算法 - IP段拆分合并（IPHandle.init）：**
```
输入：IP信息列表（含起始/结束IP）、IP版本
处理：
  1. 将每个IP段的起始/结束地址转换为事件节点（GapRangeNode）
  2. 按IP数值排序所有事件节点
  3. 扫描线算法遍历事件节点：
     - 遇到起始节点：将对应IP信息加入当前活跃集合
     - 遇到结束节点：将对应IP信息从活跃集合移除
     - 在相邻节点间生成输出段（OutputNode）
  4. 每个输出段携带当前活跃集合中的所有IP信息
输出：拆分后的IP段列表（OutputNode）
```

**实体类：**
- `GapRangeNode`：事件节点（IP数值、索引、是否结束标志）
- `IpInfoBase` / `IpInfo` / `IpInfoNode`：IP信息实体
- `IpAddressRange`：IP地址范围
- `IpMergeResult`：IP合并结果
- `OutputNode`：输出节点（起始IP、结束IP、关联的IP信息集合）

##### 3.2.2.3 ngfa-spring-boot-starter-report（报表组件）

**功能：** 动态配置转实体、报表引擎基础

**核心类：**
- `ConfigToEntityApi`：配置转实体REST接口，支持运行时动态更新配置
- `ConfigToEntity`：配置解析工具
- `BaseEntityConfig`：基础实体配置
- `ReportMapper`：报表数据访问层
- `ReportRequest` / `ReportResponse`：报表请求/响应封装

**实现逻辑：**
```
配置读取 → 反射解析 → 实体映射 → 动态更新
支持通过PUT接口按路径更新嵌套配置属性
```

##### 3.2.2.4 ngfa-spring-boot-starter-log（日志组件）

**功能：** 操作日志自动记录

**核心类：**
- `OperationLog`：操作日志注解
- `OperationModel`：操作模型注解
- `OperationLogAspect`：AOP切面，拦截带注解的方法自动记录日志
- `OperationLogMapper`：日志数据访问
- `OperationLogLayout` / `TraceFormatLayout`：日志格式化

**实现逻辑：**
```
方法调用 → @Before解析注解参数 → 记录请求信息
         → @After记录执行结果 → 持久化到数据库
         → @AfterThrowing记录异常信息
```

**建表SQL：** `resources/sql/create_table.sql`

##### 3.2.2.5 ngfa-spring-boot-starter-exception（异常组件）

**功能：** 统一异常处理

**核心类：**
- `BaseErrorCode` / `GeneralErrorCode`：错误码定义
- `BaseException` / `BusException` / `HttpException` / `ForbiddenException`：自定义异常
- `GlobalControllerAdvice`：全局异常处理器
- `BusinessExceptionAssert`：业务断言

**异常处理流程：**
```
业务异常 → BusException → GlobalControllerAdvice捕获
                         → 国际化消息解析（i18n）
                         → 统一格式响应
```

##### 3.2.2.6 ngfa-spring-boot-starter-dic（数据字典组件）

**功能：** 数据字典管理

**核心类：**
- `DicController`：字典API控制器
- `DistrictDicApi`：行政区划字典API
- `DictionaryInterceptor`：字典拦截器
- `SysMultiDic`：多值字典实体
- `DistrictAddressIdInfo`：行政区划地址信息

##### 3.2.2.7 ngfa-spring-boot-starter-easyApi（通用API组件）

**功能：** 低代码通用CRUD接口

**核心类：**
- `GeneralApi`：通用API基类
- `GeneralMapper`：通用Mapper
- `IGeneralService`：通用服务接口
- `MyBatisPlusConfig`：MyBatis-Plus配置

##### 3.2.2.8 ngfa-spring-boot-starter-sftp（SFTP组件）

**功能：** SFTP文件操作

**核心接口：** `SftpFileService`
- `downloadFile`：下载单个文件
- `downloadFileFolder`：下载整个目录
- `uploadFile`：上传文件
- `downloadMatchFiles`：按模式匹配批量下载
- `removeRemoteFile`：删除远程文件
- `copyFileToDailyReport`：复制到日报目录

##### 3.2.2.9 ngfa-spring-boot-starter-snmpClient（SNMP组件）

**功能：** SNMP网络协议客户端

**核心类：**
- `SnmpClientService`：SNMP客户端服务
  - `snmpGet`：单属性采集
  - `snmpGetBulk`：批量采集（GETBULK）
  - `snmpWalk`：遍历采集
  - `targetInit`：目标初始化（支持v1/v2c/v3）
- `SnmpRequest`：SNMP请求封装
- `AesUtil`：AES加密工具（SNMPv3加密）

**支持协议版本：** SNMPv1、SNMPv2c、SNMPv3（含认证加密）

---

### 3.3 ngfa-cloud-gateway（网关服务）

#### 3.3.1 模块定位
系统统一入口，提供路由转发、认证鉴权。

#### 3.3.2 核心配置

**路由规则：**

| 路由ID | 目标服务 | 匹配路径 |
|--------|---------|---------|
| ngfa-cloud-dataConfig | lb://ngfa-cloud-dataConfig | /dataConfig/** |
| ngfa-cloud-dataReport | lb://ngfa-cloud-dataReport | /dataReport/** |
| ngfa-cloud-alarm | lb://ngfa-cloud-alarm | /alarm/** |
| ngfa-cloud-sso | lb://ngfa-cloud-sso | /sso/** |
| ngfa-cloud-GPT | lb://ngfa-cloud-GPT | /gpt/** |
| ngfa-cloud-dataProcessor | lb://ngfa-cloud-dataProcessor | /dataProcessor/** |
| ngfa-cloud-ipAnalyse | lb://ngfa-cloud-ipAnalyse | /ipAnalyse/** |

**免认证URL：** `/test1/**`、`/sso/fourA/**`、`/dataProcessor/radiusDatas/**`

#### 3.3.3 技术实现
- 基于Spring Cloud Gateway（WebFlux响应式）
- OAuth2资源服务器（Opaque Token模式）
- Nacos服务发现
- OpenFeign声明式调用
- 端口：8083，上下文路径：/gateway

---

### 3.4 ngfa-cloud-service（微服务）

#### 3.4.1 ngfa-cloud-dataAccess（数据采集服务）

**模块定位：** 负责从网络设备和外部系统采集原始数据

**核心功能：**
- SNMP数据采集（路由器端口流量）
- BGP路由数据文件采集（SFTP下载+文件解析）
- 数据推送至Kafka

**关键类：**

| 类 | 功能 |
|----|------|
| `CollectTaskJob` | XXL-JOB定时任务（SNMP采集、BGP同步、配置清理） |
| `SyncApi` | 手动同步触发接口 |
| `DataIngestionAdapterRunner` | SNMP数据采集适配器 |
| `DataIngestionBgpAdapterRunner` | BGP数据采集适配器 |
| `DataAccessConfig` | 数据采集配置 |
| `KafkaSendConfig` | Kafka发送配置 |
| `ThreadPoolConfig` | 线程池配置 |

**定时任务：**
- `collectJob`：SNMP数据采集
- `snmpClean`：SNMP配置清理
- `snmpConfig`：SNMP配置采集
- `syncBgp`：BGP文件同步

**数据实体：**
- `SnmpRouter`：SNMP路由器配置
- `SnmpConfigurationInfo`：SNMP配置信息
- `RouterOidRelation`：路由器OID关系
- `ASNumberUnionBgpPO`：AS号联合BGP
- `Atm`：ATM数据
- `CityGroupIndexInfo`：城市分组索引

#### 3.4.2 ngfa-cloud-dataConfig（数据配置服务）

**模块定位：** 系统配置数据管理

**核心功能：**
- BGP路由数据配置
- 路由器端口配置
- 采样率配置
- 客户地址数据管理
- 结算IP信息管理
- 拆分合并规则配置

**关键配置项（Mapper XML）：**
- `DownLoadBGPRouteDateMapper`：BGP路由数据下载
- `DownLoadCYWAndIDCAddressDataMapper`：CYW和IDC地址数据
- `DownLoadIDCCustomerAddressDataMapper`：IDC客户地址数据
- `RouterPortBaseDataMapper`：路由器端口基础数据
- `RouterPortFlowMapper`：路由器端口流量
- `RouterPortRuleMapper`：路由器端口规则
- `SplitMergeCustomerMapper`：客户拆分合并
- `SplitMergeTyyCdnMapper`：天翼云CDN拆分合并
- `FibSampRateInfoMapper`：FIB采样率
- `FlowSettlementInterprovincialMapper`：省际结算流量
- `FlowSettlementProvinceMapper`：省内结算流量

#### 3.4.3 ngfa-cloud-dataProcessor（数据处理服务）

**模块定位：** 数据加工处理

**核心功能：**
- 应用域名数据处理
- 网络摄像头DNS数据处理
- PCDN DNS数据处理
- PCDN用户数据处理
- Radius数据处理

**关键Mapper：**
- `AppyDomainDataMapper`：应用域名数据
- `NetworkCameraDnsDataMapper`：网络摄像头DNS
- `PcdnDnsDataMapper`：PCDN DNS
- `PcdnUserDataMapper`：PCDN用户
- `RadiusDataMapper`：Radius数据

**特殊配置：** 注册了ClickHouse方言（复用MySQL方言）

#### 3.4.4 ngfa-cloud-alarm（告警服务）

**模块定位：** 系统告警管理

**核心功能：**
- 告警规则配置
- 告警触发与通知
- 告警历史查询

#### 3.4.5 ngfa-cloud-GPT（GPT服务）

**模块定位：** AI智能分析服务

**核心功能：**
- 智能问答
- 数据分析辅助

#### 3.4.6 ngfa-cloud-dailyReport（日报服务）

**模块定位：** 日报自动生成

**核心功能：**
- 日报数据汇总
- Excel报表生成
- SFTP上传分发

#### 3.4.7 ngfa-cloud-dataComparison / ngfa-cloud-ipAnalyse（IP分析服务）

**模块定位：** IP地址拆分合并分析

**核心功能：**
- IP地址段拆分
- IP地址段合并
- IP冲突检测

---

### 3.5 ngfa-cloud-module（业务模块）

#### 3.5.1 模块结构模式

所有业务模块遵循统一的 `Config + Report` 双模块模式：
- **Config模块**（xxxConfig）：配置数据管理
- **Report模块**（xxxReport）：报表数据分析

每个模块又分为 `api`（实现层）和 `sdk`（接口层）两个子模块。

#### 3.5.2 ngfa-cloud-flow（流量分析模块）

**模块定位：** 核心流量分析功能

**flowConfig（流量配置）：**
- AS号区分信息管理
- 城市/省份编码管理
- IDC客户区域管理
- 路由器信息管理
- BGP信息优化
- 学习数据管理（LearnData）
- 月账单管理

**关键Mapper（20+）：**
- `AsNumAndBgpImproveInfoMapper`：AS号与BGP优化
- `AsNumberDistinguishInfoMapper`：AS号区分
- `AsTypeMapMapper`：AS类型映射
- `BusinessUserIpMapper`：商业用户IP
- `CityCodeMapper` / `CityProvinceMapper`：城市编码
- `CtmCustomerInfoMapper`：CTM客户信息
- `IDCCustomerRegionMapper`：IDC客户区域
- `IDCSplitMergeIPMapper`：IDC拆分合并IP
- `ImproveBgpInfoMapper`：BGP优化信息
- `LearnDataInfoMapper` / `LearnIpMergeManIdcInfoMapper`：学习数据
- `RouterInfoMapper` / `SnmpRouterMapper`：路由器信息
- `ProvinceCodeMapper` / `ProvinceInfoMapper`：省份信息

**flowReport（流量报表）：**
- 客户流量统计
- 客户报表生成
- 区域流量分析
- IDC流量趋势分析
- 省际流量分析
- 域名应用信息
- PCDN域名信息

**关键Mapper（14个）：**
- `CustomerFlowMapper` / `CustomerReportMapper`：客户流量报表
- `DistrictAddressInfoMapper` / `DistrictAddressIpMapper`：区域地址
- `DistrictOverViewMapper` / `DistrictToProvMapper`：区域概览
- `IdcReportMapper` / `IdcTrendyAnalysisMapper`：IDC报表
- `OverViewMapper`：总览
- `ProvToProvMapper`：省际流量
- `RouterDomainInfoMapper`：路由器域名
- `DomainApplyInfoMapper`：域名申请

#### 3.5.3 ngfa-cloud-pcdn（PCDN分析模块）

**模块定位：** PCDN（P2P CDN）流量分析

**pcdnConfig（PCDN配置）：**
- 家庭用户IP管理

**pcdnReport（PCDN报表）：**
- PCDN总览
- PCDN数据分析
- PCDN疑似用户
- 用户域名分析
- 用户目的流量分析
- 用户目的端口分析
- 用户源端口分析
- 用户协议分析
- 上下行分析

**关键Mapper（11个）：**
- `pcdn/OverviewMapper` / `pcdn/PcdnOverviewMapper`：PCDN总览
- `pcdn/PcdnDataMapper`：PCDN数据
- `pcdn/PcdnSuspectedUserMapper`：疑似用户
- `pcdn/PcdnUserDomainMapper`：用户域名
- `pcdn/PcdnUserDstFlowMapper`：目的流量
- `pcdn/PcdnUserDstPortMapper`：目的端口
- `pcdn/PcdnUserSrcPortMapper`：源端口
- `pcdn/PcdnUserProtocolMapper`：协议分析
- `pcdn/PcdnUserFlowMapper`：用户流量
- `PcdnMapper` / `UpAndDownMapper`：PCDN主表/上下行

#### 3.5.4 ngfa-cloud-app（应用分析模块）

**模块定位：** 应用层流量分析

**appConfig（应用配置）：** 应用配置管理

**appReport（应用报表）：**
- 应用总览
- 应用详情
- 应用域名详情

#### 3.5.5 ngfa-cloud-video（视频分析模块）

**模块定位：** 视频流量分析

**videoConfig（视频配置）：** 网络摄像头域名管理

**videoReport（视频报表）：** 视频流量统计

#### 3.5.6 ngfa-cloud-glove（白手套分析模块）

**模块定位：** 白手套业务分析

**gloveConfig（白手套配置）：** 签约客户信息管理

**gloveReport（白手套报表）：**
- 云应用信息维度
- DNS数据分析
- 白手套用户分析

#### 3.5.7 ngfa-cloud-market（市场分析模块）

**模块定位：** 市场流量分析

**marketReport（市场报表）：** 云市场流量分析（NetflowCloud）

#### 3.5.8 ngfa-cloud-otherNetwork（其他网络分析模块）

**模块定位：** 其他网络类型分析

**otherNetworkReport（其他网络报表）：** 其他网络流量统计

#### 3.5.9 ngfa-cloud-pullFlow（拉流分析模块）

**模块定位：** 拉流业务分析

**pullFlowReport（拉流报表）：** 拉流流量统计

---

## 四、模块依赖关系

### 4.1 依赖关系图

```
                          ┌─────────────────────┐
                          │  ngfa-cloud-parent   │
                          │   (父POM版本管理)     │
                          └──────────┬──────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
    ┌─────────▼─────────┐ ┌─────────▼─────────┐ ┌─────────▼─────────┐
    │  ngfa-cloud-base   │ │ngfa-cloud-framework│ │ngfa-cloud-gateway │
    │   (基础工具层)      │ │  (技术组件层)       │ │   (网关层)         │
    └─────────┬─────────┘ └─────────┬─────────┘ └───────────────────┘
              │                      │
              │    ┌─────────────────┘
              │    │
    ┌─────────▼────▼──────────────────────────────────────┐
    │              ngfa-cloud-service (微服务层)            │
    │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
    │  │dataAccess│ │dataConfig│ │dataProces.│            │
    │  │ (采集)    │ │ (配置)    │ │ (处理)    │            │
    │  └──────────┘ └──────────┘ └──────────┘            │
    │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
    │  │  alarm   │ │   GPT    │ │dailyReport│            │
    │  │ (告警)    │ │ (AI)     │ │ (日报)    │            │
    │  └──────────┘ └──────────┘ └──────────┘            │
    └─────────────────────────────────────────────────────┘
              │
    ┌─────────▼───────────────────────────────────────────┐
    │              ngfa-cloud-module (业务模块层)           │
    │  ┌──────┐ ┌──────┐ ┌─────┐ ┌──────┐ ┌──────┐      │
    │  │ flow │ │ pcdn │ │ app │ │video │ │glove │      │
    │  └──────┘ └──────┘ └─────┘ └──────┘ └──────┘      │
    │  ┌──────┐ ┌───────────┐ ┌────────┐                 │
    │  │market│ │otherNetwork│ │pullFlow│                 │
    │  └──────┘ └───────────┘ └────────┘                 │
    └─────────────────────────────────────────────────────┘
```

### 4.2 依赖矩阵

| 模块 | base | auth | ip | report | log | exception | sftp | snmp | dic | easyApi |
|------|------|------|-----|--------|-----|-----------|------|------|-----|---------|
| gateway | - | Y | - | - | - | - | - | - | - | - |
| dataAccess | Y | - | - | - | Y | Y | Y | Y | - | - |
| dataConfig | Y | - | - | - | Y | Y | - | - | - | - |
| dataProcessor | Y | - | - | - | Y | Y | - | - | - | - |
| alarm | Y | - | - | - | Y | Y | - | - | - | - |
| GPT | Y | - | - | - | Y | Y | - | - | - | - |
| dailyReport | Y | - | - | - | Y | Y | - | - | - | - |
| flow | Y | - | Y | Y | Y | Y | - | - | - | - |
| pcdn | Y | - | Y | Y | Y | Y | - | - | - | - |
| app | Y | - | - | Y | Y | Y | - | - | - | - |
| video | Y | - | - | Y | Y | Y | - | - | - | - |
| glove | Y | - | - | Y | Y | Y | - | - | - | - |
| market | Y | - | - | Y | Y | Y | - | - | - | - |
| otherNetwork | Y | - | - | Y | Y | Y | - | - | - | - |
| pullFlow | Y | - | - | Y | Y | Y | - | - | - | - |

---

## 五、核心业务流程

### 5.1 数据采集流程

```
┌──────────┐    SNMP     ┌──────────────┐    Kafka    ┌────────────────┐    入库    ┌──────────┐
│ 网络设备   │ ──────────→ │  dataAccess   │ ──────────→ │ dataProcessor  │ ─────────→ │ 数据库    │
│ (路由器)   │            │  (SNMP采集)   │            │  (数据处理)     │            │ (CK/MySQL)│
└──────────┘            └──────────────┘            └────────────────┘            └──────────┘

┌──────────┐    SFTP     ┌──────────────┐   解析入库   ┌──────────┐
│ BGP文件   │ ──────────→ │  dataAccess   │ ──────────→ │ 数据库    │
│ (外部系统) │            │  (文件下载)   │            │          │
└──────────┘            └──────────────┘            └──────────┘
```

### 5.2 流量分析流程

```
┌──────────┐   查询配置   ┌──────────────┐   IP拆分合并  ┌──────────────┐   报表生成   ┌──────────┐
│ 数据库    │ ──────────→ │  flowConfig   │ ──────────→ │  flowReport   │ ──────────→ │ 前端展示  │
│ (配置数据) │            │  (配置管理)   │            │  (报表分析)    │            │          │
└──────────┘            └──────────────┘            └──────────────┘            └──────────┘
```

### 5.3 告警流程

```
┌──────────┐   阈值监控   ┌──────────────┐   告警通知   ┌──────────┐
│ 数据监控   │ ──────────→ │   alarm      │ ──────────→ │ 短信/邮件  │
│          │            │  (告警判断)   │            │          │
└──────────┘            └──────────────┘            └──────────┘
```

### 5.4 日报生成流程

```
┌──────────┐   定时触发   ┌──────────────┐   数据汇总   ┌──────────────┐   SFTP上传  ┌──────────┐
│ XXL-JOB  │ ──────────→ │ dailyReport  │ ──────────→ │ Excel生成    │ ──────────→ │ 文件服务器│
│          │            │  (日报服务)   │            │              │            │          │
└──────────┘            └──────────────┘            └──────────────┘            └──────────┘
```

### 5.5 认证鉴权流程

```
┌──────────┐  请求+Token  ┌──────────────┐  Opaque Token  ┌──────────────┐
│ 客户端    │ ──────────→ │   gateway    │ ────────────→ │  IAM服务      │
│          │            │  (网关)       │  内省校验      │ (认证中心)    │
└──────────┘            └──────┬───────┘               └──────────────┘
                              │ 路由转发
                       ┌──────▼───────┐
                       │  后端微服务    │
                       │  (业务处理)   │
                       └──────────────┘
```

---

## 六、关键技术点详解

### 6.1 IP地址拆分合并算法

这是系统的核心算法，位于 `ngfa-spring-boot-starter-ip` 组件。

**算法描述：** 扫描线算法（Sweep Line Algorithm）

**输入：** N个IP段，每个IP段关联一组IP信息（如客户、区域等）

**输出：** M个不重叠的IP段，每个段携带所有覆盖它的IP信息集合

**时间复杂度：** O(N log N)（排序主导）

**应用场景：**
- 多客户IP段重叠时的流量归属分析
- IDC/城域网IP段冲突检测
- IP白名单与黑名单交叉分析

### 6.2 SNMP数据采集

**协议版本：** 支持SNMPv1/v2c/v3

**采集方式：**
- GET：单属性采集
- GETBULK：批量属性采集（高效）
- WALK：遍历采集（MIB树遍历）

**SNMPv3安全特性：**
- 认证协议：MD5/SHA
- 加密协议：DES/AES
- 用户名/密码/加密密钥配置

### 6.3 Kafka消息流转

**消息主题：**
- `TOPIC_BIG_DATA`：大数据通知
- 各业务Topic：流量数据、配置变更等

**异步推送：** 基于CompletableFuture的非阻塞发送

**消费监控：** `KafkaConsumerGroupOffsetChecker` 检查消费组偏移量

### 6.4 动态配置引擎

**实现方式：** 反射 + 配置绑定

**功能：**
- 运行时读取YAML配置为实体对象
- 通过REST API动态更新配置属性
- 支持嵌套路径更新（如 `config.report.threshold`）

### 6.5 统一异常处理

**处理链：**
```
异常发生 → GlobalControllerAdvice捕获
         → 异常类型判断（业务异常/参数异常/系统异常）
         → i18n国际化消息解析
         → 统一格式响应
```

**支持的异常类型：**
- `BusException`：业务异常
- `HttpException`：HTTP异常
- `ForbiddenException`：权限异常
- `MethodArgumentNotValidException`：参数校验异常
- `IllegalArgumentException`：非法参数

### 6.6 操作日志AOP

**切面逻辑：**
1. `@Before`：解析 `@OperationLog` 注解，记录请求参数
2. `@After`：记录执行结果
3. `@AfterThrowing`：记录异常信息
4. 日志持久化到数据库

**日志内容：** 操作人、操作时间、请求URL、请求参数、响应结果、执行耗时

---

## 七、系统架构特点

### 7.1 架构优势

1. **微服务拆分合理**：按业务功能（流量/PCDN/应用等）和职责（配置/报表/采集/处理）双维度拆分
2. **技术组件复用**：公共功能抽取为Starter组件，避免重复开发
3. **可扩展性强**：模块化设计，新增业务只需添加新Module
4. **高可用设计**：Nacos服务发现 + 负载均衡 + 异步消息 + 分布式任务
5. **数据安全**：配置加密（Jasypt）+ OAuth2认证 + 操作日志审计

### 7.2 数据流架构

```
外部数据源 → 采集层(dataAccess) → 消息层(Kafka) → 处理层(dataProcessor) → 存储层(MySQL/CK)
                                                                              │
                                                              ┌───────────────┘
                                                              ▼
前端展示 ← 网关(gateway) ← 报表层(module/report) ← 分析引擎(IP处理/统计)
```

### 7.3 部署架构

- **容器化部署**：各服务提供Dockerfile
- **服务注册**：Nacos（地址：172.21.6.106:30659）
- **链路追踪**：SkyWalking Agent
- **配置管理**：Nacos Config + 本地配置文件（dev/test/pro多环境）

---

## 八、版本历史

### V1.0.0_beta
- IDC客户流量分析
- TopIp流量分析
- 数据可视化
- 低代码框架

### V1.7.0_beta
- PCDN流量分析模块

---

## 九、附录

### 9.1 配置文件说明

各服务配置文件位于 `config/` 目录，支持多环境：
- `application-dev.yml`：开发环境
- `application-test.yml`：测试环境
- `application-pro.yml`：生产环境
- `application.yml`：默认配置

### 9.2 国际化资源

各服务提供 `i18n/` 目录下的中文消息资源：
- `general_message_zh_CN.properties`：通用消息
- `alarm_message_zh_CN.properties`：告警消息
- `access_message_zh_CN.properties`：采集消息
- `config_message_zh_CN.properties`：配置消息
- `report_message_zh_CN.properties`：报表消息
- `gpt_message_zh_CN.properties`：GPT消息
- 各模块自定义消息文件

### 9.3 端口分配

| 服务 | 端口 |
|------|------|
| gateway | 8083 |
| 其他服务 | Nacos动态分配 |
