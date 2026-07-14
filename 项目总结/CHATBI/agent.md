# Chat 模块 - 智能语义对话引擎

## 一、模块概述

`chat` 是 `supersonic` 项目中的核心业务模块，实现了一个**基于大语言模型（LLM）的智能语义对话引擎**。它将用户的自然语言查询转化为结构化的 SQL 查询语句或第三方插件调用，并返回结果。

采用**基于 Agent 的架构**，集成了以下核心能力：
- **NL2SQL**：自然语言转 SQL 查询
- **多轮对话**：结合历史上下文的对话改写
- **插件系统**：支持第三方插件扩展
- **记忆增强**：通过 LLM 自动评估 SQL 质量，构建记忆库
- **权限管理**：基于用户和角色的权限控制

### 项目结构

```
chat/
├── pom.xml                          # 父 POM，聚合 api 和 server 子模块
├── api/                             # API 接口层（请求/响应对象）
│   └── pom.xml
└── server/                          # 服务端核心实现
    ├── pom.xml
    └── src/main/
        ├── java/com/tencent/supersonic/chat/server/
        │   ├── agent/               # Agent 模型定义
        │   ├── config/              # 聊天配置模型
        │   ├── executor/            # 查询执行器
        │   ├── memory/              # 记忆评估任务
        │   ├── parser/              # 自然语言解析器
        │   ├── plugin/              # 插件系统
        │   ├── pojo/                # 内部 POJO
        │   ├── processor/           # 结果处理器
        │   ├── rest/                # REST 控制器
        │   ├── service/             # 服务接口层
        │   └── util/                # 工具类
        └── resources/mapper/        # MyBatis XML 映射
```

---

## 二、文件清单

| 层级 | 包路径 | 文件 | 数量 |
|------|--------|------|------|
| 配置 | - | `pom.xml` (父、api、server) | 3 |
| 模型 | `agent/` | `Agent.java`, `AgentTool.java`, `AgentToolType.java`, `DatasetTool.java`, `PluginTool.java`, `ToolConfig.java`, `VisualConfig.java` | 7 |
| 模型 | `config/` | `ChatConfig.java`, `ChatConfigFilterInternal.java` | 2 |
| 模型 | `pojo/` | `ChatContext.java`, `ChatMemory.java`, `ExecuteContext.java`, `ParseContext.java` | 4 |
| 接口 | `parser/` | `ChatQueryParser.java`, `NL2SQLParser.java`, `NL2PluginParser.java`, `PlainTextParser.java` | 4 |
| 接口 | `executor/` | `ChatQueryExecutor.java`, `PlainTextExecutor.java`, `PluginExecutor.java`, `SqlExecutor.java` | 4 |
| 接口 | `processor/` | `ResultProcessor.java` | 1 |
| 插件 | `plugin/` | `ChatPlugin.java`, `ParseMode.java`, `PluginManager.java`, `PluginParseConfig.java`, `PluginParseResult.java`, `PluginQueryManager.java`, `PluginRecallResult.java` | 7 |
| 控制器 | `rest/` | `AgentController.java`, `ChatConfigController.java`, `ChatController.java`, `ChatQueryController.java`, `MemoryController.java`, `PluginController.java` | 6 |
| 服务 | `service/` | `AgentService.java`, `ChatContextService.java`, `ChatManageService.java`, `ChatQueryService.java`, `ConfigService.java`, `MemoryService.java`, `PluginService.java`, `RecommendService.java`, `StatisticsService.java` | 9 |
| 工具 | `util/` | `ChatConfigHelper.java`, `ComponentFactory.java`, `QueryReqConverter.java`, `ResultFormatter.java` | 4 |
| 任务 | `memory/` | `MemoryReviewTask.java` | 1 |
| 映射 | `mapper/` | `ChatMapper.xml`, `ChatParseMapper.xml`, `ChatConfigMapper.xml`, `ChatContextMapper.xml`, `StatisticsMapper.xml`, `ShowCaseCustomMapper.xml` | 6 |
| **总计** | | | **54** |

---

## 三、模块功能说明

### 3.1 Agent 模块（`agent/`）

#### Agent（智能体）
一个智能体代表一个对话助手，是整个系统的核心实体。

**关键属性：**
| 属性 | 类型 | 说明 |
|------|------|------|
| `id` | Integer | 唯一标识 |
| `name` | String | 名称 |
| `description` | String | 描述 |
| `status` | Integer | 0=离线, 1=在线 |
| `enableSearch` | Integer | 是否启用搜索 |
| `enableFeedback` | Integer | 是否启用反馈 |
| `toolConfig` | String | JSON 格式的工具配置 |
| `chatAppConfig` | Map<String, ChatApp> | LLM 应用配置 |
| `visualConfig` | VisualConfig | 可视化配置 |

**核心方法：**
- `getTools(AgentToolType)`：获取指定类型的工具列表
- `containsDatasetTool()`：是否包含数据集工具
- `containsPluginTool()`：是否包含插件工具
- `getDataSetIds()`：获取关联的所有数据集 ID
- `enableMemoryReview()`：是否启用记忆评估

#### AgentToolType（工具类型枚举）
| 枚举值 | 说明 |
|--------|------|
| `DATASET` | Text2SQL 数据集，用于 NL2SQL 解析 |
| `PLUGIN` | 第三方插件，用于插件调用 |

#### 工具类继承关系
```
AgentTool (基类: id, name, type)
├── DatasetTool (扩展: dataSetIds, exampleQuestions)
└── PluginTool  (扩展: plugins)
```

---

### 3.2 Config 模块（`config/`）

配置数据集的聊天行为，包括明细查询配置、聚合查询配置和推荐问题列表。

**ChatConfig 核心属性：**
| 属性 | 类型 | 说明 |
|------|------|------|
| `id` | Long | 主键 |
| `modelId` | Long | 关联的数据模型 ID |
| `chatDetailConfig` | ChatDetailConfigReq | 明细查询配置 |
| `chatAggConfig` | ChatAggConfigReq | 聚合查询配置 |
| `recommendedQuestions` | List<RecommendedQuestionReq> | 推荐问题列表 |
| `status` | StatusEnum | 可用状态 |

---

### 3.3 Parser 模块（`parser/`）

四种解析器实现了 `ChatQueryParser` 接口，采用策略模式组织。

#### 解析器一览

| 解析器 | 功能 | 触发条件 |
|--------|------|----------|
| **PlainTextParser** | 纯文本解析 | Agent 不包含任何工具时 |
| **NL2SQLParser** | 自然语言→SQL 解析 | Agent 包含数据集工具 |
| **NL2PluginParser** | 自然语言→插件调用 | Agent 包含插件工具 |

#### NL2SQLParser 核心流程

```
NL2SQLParser.parse()
  │
  ├─ 1. 检查是否启用 NL2SQL
  │
  ├─ 2. 规则解析阶段（用户未选择解析时）
  │     ├─ 遍历每个数据集
  │     ├─ 按 STRICT → MODERATE → LOOSE 模式逐步匹配
  │     ├─ 每个数据集取 Top 1 解析结果
  │     └─ 合并所有数据集结果，按分数排序取 Top N
  │
  ├─ 3. LLM 解析阶段（需要 LLM 且不需要用户反馈时）
  │     ├─ 多轮对话改写（如果启用）
  │     ├─ 动态示例召回（从向量数据库）
  │     └─ 调用 LLM 生成 SQL
  │
  └─ 4. 失败时回退：使用 ALL 模式重新解析
```

#### 多轮对话改写逻辑

```
rewriteMultiTurn()
  │
  ├─ 1. 获取当前问题的语义映射结果
  ├─ 2. 获取最近 1 条成功的历史查询
  ├─ 3. 构建设置变量：
  │     ├─ current_question：当前问题
  │     ├─ current_schema：当前映射的指标/维度/值
  │     ├─ history_question：历史问题
  │     ├─ history_schema：历史映射的指标/维度/值
  │     └─ history_sql：历史 SQL
  └─ 4. 调用 LLM 生成改写后的问题
```

---

### 3.4 Executor 模块（`executor/`）

三种执行器实现了 `ChatQueryExecutor` 接口，根据解析结果执行查询。

#### 执行器一览

| 执行器 | 功能 | 执行方式 |
|--------|------|----------|
| **PlainTextExecutor** | 闲聊对话 | 直接调用 LLM 生成回复 |
| **PluginExecutor** | 执行插件查询 | 委托给 PluginSemanticQuery |
| **SqlExecutor** | 执行 SQL 查询 | 调用语义层执行 SQL 并创建记忆 |

#### SqlExecutor 执行流程

```
SqlExecutor.execute()
  │
  ├─ 1. 获取聊天上下文
  ├─ 2. 验证解析信息中的 SQL 是否有效
  ├─ 3. 构建 QuerySqlReq 请求
  ├─ 4. 调用语义层执行 SQL 查询
  ├─ 5. 格式化查询结果为文本
  ├─ 6. 如果查询成功且为 LLMSqlQuery 模式：
  │     └─ 创建记忆记录（ChatMemory）
  └─ 7. 返回 QueryResult
```

---

### 3.5 Plugin 模块（`plugin/`）

#### PluginManager（插件管理器）

核心功能：
1. **插件识别**：通过 Embedding 向量检索，将用户问题与插件示例匹配
2. **插件解析**：通过 `resolve()` 方法验证插件参数与语义映射的匹配度
3. **生命周期管理**：通过事件监听处理插件的增删改

#### 插件识别流程

```
PluginManager → PluginRecognizer.recognize()
  │
  ├─ 1. 获取 Agent 可用的插件列表
  ├─ 2. 对用户问题进行 Embedding 向量检索
  ├─ 3. 匹配插件示例问题
  ├─ 4. 验证插件参数与语义映射的匹配度
  │     ├─ 检查数据集是否匹配
  │     ├─ 检查 SEMANTIC 类型参数是否在语义映射中
  │     └─ 所有参数匹配成功才算匹配
  └─ 5. 返回匹配结果（Plugin + 数据集 ID 集合）
```

#### PluginQueryManager（插件查询注册器）

维护全局 `Map<String, PluginSemanticQuery>`，支持按 `queryMode` 注册和查询插件查询。

#### ParseMode（解析模式枚举）

| 枚举值 | 说明 |
|--------|------|
| `EMBEDDING_RECALL` | 基于 Embedding 向量召回 |
| `FUNCTION_CALL` | 基于函数调用 |

---

### 3.6 Memory 模块（`memory/`）

#### MemoryReviewTask（记忆评估定时任务）

每 60 秒执行一次，自动评估 SQL 记忆的正确性。

```
MemoryReviewTask.review()  [每60秒执行]
  │
  ├─ 1. 遍历所有 Agent
  ├─ 2. 跳过未启用记忆评估的 Agent
  ├─ 3. 遍历 Agent 的待审核记忆
  ├─ 4. 构造 LLM 评估提示（问题 + Schema + 上下文 + SQL）
  ├─ 5. 调用 LLM 获取评估结果
  ├─ 6. 解析 LLM 输出（正则匹配 opinion/comment）
  └─ 7. 如果评估为 POSITIVE，自动启用该记忆
```

**LLM 输出格式：**
```
opinion=(POSITIVE|NEGATIVE),comment=(your comment)
```

---

### 3.7 REST 控制器（`rest/`）

| 控制器 | 路由 | 功能 |
|--------|------|------|
| **AgentController** | `/api/chat/agent` 和 `/openapi/chat/agent` | Agent 的 CRUD 操作 |
| **ChatConfigController** | `/api/chat/conf` 和 `/openapi/chat/conf` | 聊天配置管理 |
| **ChatController** | `/api/chat/manage` 和 `/openapi/chat/manage` | 会话管理（增删改查、反馈） |
| **ChatQueryController** | `/api/chat/query` 和 `/openapi/chat/query` | 核心查询（搜索、解析、执行） |
| **MemoryController** | `/api/chat/memory` | 记忆管理（CRUD、分页查询） |
| **PluginController** | `/api/chat/plugin` | 插件管理（CRUD、查询） |

#### API 端点详述

**AgentController：**
| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/chat/agent` | 创建 Agent |
| PUT | `/api/chat/agent` | 更新 Agent |
| DELETE | `/api/chat/agent/{id}` | 删除 Agent |
| GET | `/api/chat/agent/getAgentList` | 获取 Agent 列表 |
| GET | `/api/chat/agent/getToolTypes` | 获取工具类型 |

**ChatQueryController：**
| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/chat/query/search` | 搜索推荐 |
| POST | `/api/chat/query/parse` | 解析自然语言 |
| POST | `/api/chat/query/execute` | 执行查询 |
| POST | `/api/chat/query/` | 解析并执行（一步完成） |
| POST | `/api/chat/query/queryData` | 查询数据 |
| POST | `/api/chat/query/queryDimensionValue` | 查询维度值 |

---

### 3.8 Service 接口（`service/`）

| 服务接口 | 职责描述 |
|----------|----------|
| **ChatQueryService** | 核心查询编排：搜索→解析→执行 |
| **ChatManageService** | 会话和查询记录管理 |
| **AgentService** | Agent 的 CRUD 和权限管理 |
| **ConfigService** | 数据集聊天配置维护 |
| **MemoryService** | 记忆的增删改查 |
| **PluginService** | 插件的 CRUD 和查询 |
| **RecommendService** | 推荐问题服务 |
| **StatisticsService** | 统计数据持久化 |
| **ChatContextService** | 聊天上下文管理 |

---

## 四、关键代码逻辑解析

### 4.1 核心查询流程

```
用户输入
    │
    ▼
ChatQueryController.parse() → ChatQueryService.parse()
    │
    ▼
ComponentFactory.getChatParsers()  (SPI 加载所有解析器)
    │
    ├── PlainTextParser: Agent 无工具时，直接返回文本模式
    │
    ├── NL2PluginParser: Agent 包含插件时，执行插件识别
    │
    └── NL2SQLParser: Agent 包含数据集时，执行 NL2SQL
    │
    ▼
ParseContext (包含解析结果)
    │
    ▼
ChatQueryController.execute() → ChatQueryService.execute()
    │
    ▼
ComponentFactory.getChatExecutors()  (SPI 加载所有执行器)
    │
    ├── PlainTextExecutor: 调用 LLM 生成闲聊回复
    │
    ├── PluginExecutor: 执行插件查询
    │
    └── SqlExecutor: 调用语义层执行 SQL 并创建记忆
    │
    ▼
ExecuteContext → QueryResult (返回给用户)
```

### 4.2 组件工厂模式

`ComponentFactory` 使用 Spring 的 `SpringFactoriesLoader` 实现 SPI 机制：

```java
// 从 classpath 下的 META-INF/spring.factories 中加载实现类
private static <T> List<T> init(Class<T> factoryType, List list) {
    list.addAll(SpringFactoriesLoader.loadFactories(factoryType,
        Thread.currentThread().getContextClassLoader()));
    return list;
}
```

支持动态加载的组件类型：
- `ParseResultProcessor`：解析结果处理器
- `ExecuteResultProcessor`：执行结果处理器
- `ChatQueryParser`：查询解析器
- `ChatQueryExecutor`：查询执行器
- `PluginRecognizer`：插件识别器

---

## 五、数据流分析

### 5.1 请求数据流

```
HTTP Request
    │
    ▼
REST Controller (接收请求参数)
    │
    ▼
Service Layer (业务编排)
    │
    ▼
Parser Layer (自然语言解析)
    ├─ 语义映射 (Map)
    ├─ 规则解析 (STRICT → MODERATE → LOOSE)
    ├─ 多轮改写 (LLM)
    └─ 动态示例召回 (Embedding)
    │
    ▼
Executor Layer (查询执行)
    ├─ 语义层 SQL 执行
    ├─ LLM 闲聊回复
    └─ 插件调用
    │
    ▼
ResultProcessor (结果处理)
    │
    ▼
HTTP Response (QueryResult)
```

### 5.2 数据实体关系

```
Agent (智能体)
  │
  ├── ChatDO (会话)
  │     ├── chatId (PK)
  │     ├── agentId (FK → Agent.id)
  │     └── creator
  │
  ├── ChatQueryDO (查询记录)
  │     ├── questionId (PK)
  │     ├── chatId (FK → ChatDO.chatId)
  │     ├── queryResult (JSON)
  │     └── score
  │
  ├── ChatParseDO (解析记录)
  │     ├── questionId (FK → ChatQueryDO.questionId)
  │     ├── parseId
  │     └── parseInfo (JSON - SemanticParseInfo)
  │
  ├── ChatContextDO (上下文)
  │     ├── chatId (PK)
  │     └── semanticParse (JSON)
  │
  └── ChatMemory (记忆)
        ├── id (PK)
        ├── agentId (FK → Agent.id)
        ├── queryId
        ├── question / dbSchema / s2sql
        └── status / llmReviewRet / humanReviewRet
```

### 5.3 数据库表结构

| 表名 | 说明 | 核心字段 |
|------|------|----------|
| `s2_chat` | 会话表 | chat_id, agent_id, chat_name, creator, is_delete, is_top |
| `s2_chat_query` | 查询记录表 | question_id, chat_id, query_result, score, feedback, query_state |
| `s2_chat_parse` | 解析记录表 | question_id, chat_id, parse_id, parse_info, is_candidate |
| `s2_chat_context` | 上下文表 | chat_id, query_text, semantic_parse |
| `s2_chat_config` | 配置表 | model_id, chat_detail_config, chat_agg_config, status |
| `s2_chat_statistics` | 统计表 | question_id, chat_id, interface_name, cost, type |
| `s2_chat_memory` | 记忆表 | agent_id, query_id, question, s2sql, status, llm_review_ret |

---

## 六、架构设计评估

### 6.1 架构评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 模块化程度 | ★★★★★ | 清晰的模块划分，职责单一，高内聚低耦合 |
| 可扩展性 | ★★★★★ | 基于 SPI 的插件化架构，易于添加新的解析器/执行器 |
| 代码质量 | ★★★★☆ | 使用 Lombok 简化代码，但存在少量重复代码 |
| 测试覆盖 | ★★★☆☆ | 有测试依赖但未发现充分的单元测试 |

### 6.2 技术亮点

1. **SPI 扩展机制**：通过 `SpringFactoriesLoader` 实现组件自动发现，新增解析器/执行器只需添加实现类并注册即可，无需修改现有代码
2. **多阶段解析策略**：NL2SQL 采用 STRICT → MODERATE → LOOSE 三级匹配策略，兼顾精度和召回率
3. **记忆增强机制**：通过 LLM 自动评估 SQL 正确性，构建高质量的记忆库，为后续查询提供动态示例
4. **多轮对话处理**：通过 LLM 改写用户问题，解决代词指代等上下文依赖问题
5. **插件系统**：支持 Embedding 检索和语义参数匹配的双重识别机制，确保插件调用的准确性

### 6.3 潜在优化点

#### 架构层面
- **ComponentFactory 缓存刷新**：静态缓存无法在热部署时刷新，建议引入缓存失效机制
- **异常处理粒度**：控制器方法抛出 `Exception` 粒度较粗，建议定义更具体的异常类型
- **事务补偿**：SQL 执行成功后创建记忆失败可能导致数据不一致，建议引入事务补偿机制

#### 性能层面
- **多轮改写频率**：每次 LLM 解析前都调用 `rewriteMultiTurn()` 增加响应延迟，建议设置改写频率限制
- **Embedding 检索缓存**：`PluginManager.getPluginAgentCanSupport()` 每次调用都加载所有插件列表，建议引入缓存
- **记忆评估并发**：`MemoryReviewTask` 遍历所有待审核记忆，建议增加分页处理和并发控制

#### 代码层面
- **硬编码提示模板**：Prompt 模板以字符串常量定义，建议统一管理或支持外部配置
- **重复代码**：`NL2SQLParser` 和 `PlainTextExecutor` 中都实现了 `getHistoryQueries()` 方法，可提取为公共工具方法
- **ID 生成策略**：`PluginManager.generateUniqueEmbeddingId()` 中假设 num < 100，建议改为更通用的策略

---

## 七、总体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                     REST API 层 (Controllers)                     │
│  AgentController  ChatConfigController  ChatController           │
│  ChatQueryController  MemoryController  PluginController        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                     Service 层 (Interfaces)                       │
│  AgentService  ChatQueryService  ChatManageService  ConfigService│
│  MemoryService  PluginService  RecommendService  StatisticsService│
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                 核心业务逻辑层 (Core Engine)                       │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  Parsers     │  │  Executors   │  │  Plugin Manager      │   │
│  │  ├─NL2SQL    │  │  ├─SqlExec   │  │  ├─Embedding Recall  │   │
│  │  ├─NL2Plugin │  │  ├─PluginExec│  │  ├─Semantic Resolve  │   │
│  │  └─PlainText │  │  └─PlainText │  │  └─Lifecycle Manager │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │  Memory Review Task (定时任务，每60秒)                    │     │
│  └─────────────────────────────────────────────────────────┘     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    数据持久化层 (MyBatis + MySQL)                  │
│  s2_chat  s2_chat_query  s2_chat_parse  s2_chat_context         │
│  s2_chat_config  s2_chat_statistics  s2_chat_memory             │
└─────────────────────────────────────────────────────────────────┘
```
