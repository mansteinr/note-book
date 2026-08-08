# AI Agent 企业数据库安全高效接入完整技术方案：连接·认证·访问策略·防注入·连接池·异常·性能·多数据库适配

> **文档定位**:本文档是 `9AI Agent 工程实践` 系列的**数据库接入工程化专题篇**。AI Agent 要真正落地企业场景，必须能够安全、高效地读写企业核心数据资产（MySQL/PostgreSQL/Oracle/SQL Server 等）。本文档系统回答：**Agent 如何在不成为安全短板的前提下，高效接入异构数据库？**
>
> 在 [118 号企业知识库 Agent](./118企业知识库Agent系统完整工程设计方案_架构数据流模型选型接口安全开发计划与测试.md) 的"三库协同"架构、[119 号需求分析](./119企业知识库Agent项目系统性需求分析_目标用户功能非功能约束优先级验收与变更管控.md) 的 NFR-S 安全需求（PII 脱敏 0% 漏检、注入拦截 99%）之上，本文档给出**从架构设计到代码实现、从配置说明到测试验证**的端到端数据库接入工程蓝图，确保工程团队可直接据此启动开发。
>
> **核心交付物**:
> - **五层数据库接入架构**（适配层 / 连接池层 / 安全层 / 访问层 / 监控层）+ 组件交互时序
> - **三种连接方式选型对比**（JDBC / ODBC / ORM）+ 决策矩阵 + 选型推荐
> - **三层身份认证体系**（应用层 RBAC + 数据库层账号隔离 + 数据层行级权限）
> - **数据访问策略**（读写分离 / 多租户隔离 / 只读视图 / 字段级脱敏 / 限流配额）
> - **五重 SQL 注入防护**（参数化查询 + 输入校验 + 白名单 + 语义检测 + 审计回溯）
> - **连接池配置**（HikariCP / Druid 参数详解 + 调优公式 + 容灾配置）
> - **异常处理机制**（分级异常 + 重试策略 + 熔断降级 + 审计告警）
> - **性能优化方案**（索引 / 缓存 / 批量 / 异步 / 分页 / 慢查询治理）
> - **多数据库适配层**（MySQL/PostgreSQL/Oracle/SQL Server 方言适配 + SQL 方言抽象）
> - **完整代码实现**（Python SQLAlchemy + Java MyBatis 双语言示例 + 配置文件）
> - **测试验证步骤**（功能 / 安全 / 性能 / 容灾 4 类 20 项测试用例）

---

## 目录

- [一、概述：Agent 数据库接入的挑战与设计原则](#一概述agent-数据库接入的挑战与设计原则)
  - [1.1 Agent 接入数据库的四大独特挑战](#11-agent-接入数据库的四大独特挑战)
  - [1.2 八大设计原则](#12-八大设计原则)
  - [1.3 五层接入架构总览](#13-五层接入架构总览)
- [二、数据库连接方式选型](#二数据库连接方式选型)
  - [2.1 三种连接方式对比（JDBC / ODBC / ORM）](#21-三种连接方式对比jdbc--odbc--orm)
  - [2.2 ORM 框架选型决策矩阵](#22-orm-框架选型决策矩阵)
  - [2.3 选型推荐与理由](#23-选型推荐与理由)
- [三、身份认证与权限控制机制](#三身份认证与权限控制机制)
  - [3.1 三层身份认证体系](#31-三层身份认证体系)
  - [3.2 应用层 RBAC + ABAC 权限模型](#32-应用层-rbac--abac-权限模型)
  - [3.3 数据库层账号隔离策略](#33-数据库层账号隔离策略)
  - [3.4 数据层行级与列级权限控制](#34-数据层行级与列级权限控制)
- [四、数据访问策略](#四数据访问策略)
  - [4.1 读写分离架构](#41-读写分离架构)
  - [4.2 多租户数据隔离](#42-多租户数据隔离)
  - [4.3 只读视图与白名单表策略](#43-只读视图与白名单表策略)
  - [4.4 字段级脱敏与数据最小化](#44-字段级脱敏与数据最小化)
  - [4.5 限流配额与资源隔离](#45-限流配额与资源隔离)
- [五、SQL 注入防护措施](#五sql-注入防护措施)
  - [5.1 五重防护体系总览](#51-五重防护体系总览)
  - [5.2 第一重：参数化查询（必选）](#52-第一重参数化查询必选)
  - [5.3 第二重：输入校验与白名单](#53-第二重输入校验与白名单)
  - [5.4 第三重：SQL 语义安全检测](#54-第三重sql-语义安全检测)
  - [5.5 第四重：LLM 生成 SQL 的安全约束](#55-第四重llm-生成-sql-的安全约束)
  - [5.6 第五重：审计回溯与实时告警](#56-第五重审计回溯与实时告警)
- [六、连接池配置与调优](#六连接池配置与调优)
  - [6.1 连接池核心参数详解](#61-连接池核心参数详解)
  - [6.2 HikariCP 配置（Java 推荐）](#62-hikicp-配置java-推荐)
  - [6.3 SQLAlchemy 连接池配置（Python 推荐）](#63-sqlalchemy-连接池配置python-推荐)
  - [6.4 连接池容量计算公式](#64-连接池容量计算公式)
  - [6.5 连接泄漏检测与容灾配置](#65-连接泄漏检测与容灾配置)
- [七、异常处理机制](#七异常处理机制)
  - [7.1 异常分级体系](#71-异常分级体系)
  - [7.2 重试策略与退避算法](#72-重试策略与退避算法)
  - [7.3 熔断降级机制](#73-熔断降级机制)
  - [7.4 异常处理代码实现](#74-异常处理代码实现)
- [八、性能优化方案](#八性能优化方案)
  - [8.1 数据库层面优化](#81-数据库层面优化)
  - [8.2 应用层面优化](#82-应用层面优化)
  - [8.3 缓存策略](#83-缓存策略)
  - [8.4 慢查询治理](#84-慢查询治理)
- [九、多数据库适配层设计](#九多数据库适配层设计)
  - [9.1 方言适配架构](#91-方言适配架构)
  - [9.2 四种数据库方言差异对照表](#92-四种数据库方言差异对照表)
  - [9.3 SQL 方言抽象层实现](#93-sql-方言抽象层实现)
  - [9.4 分页查询适配](#94-分页查询适配)
- [十、完整代码实现](#十完整代码实现)
  - [10.1 Python 端完整实现（SQLAlchemy + 异步）](#101-python-端完整实现sqlalchemy--异步)
  - [10.2 Java 端完整实现（MyBatis + HikariCP）](#102-java-端完整实现mybatis--hikicp)
  - [10.3 配置文件说明](#103-配置文件说明)
- [十一、测试验证步骤](#十一测试验证步骤)
  - [11.1 功能测试（8 项）](#111-功能测试8-项)
  - [11.2 安全测试（6 项）](#112-安全测试6-项)
  - [11.3 性能测试（4 项）](#113-性能测试4-项)
  - [11.4 容灾测试（2 项）](#114-容灾测试2-项)
- [十二、与系列文档的集成关系](#十二与系列文档的集成关系)

---

## 一、概述：Agent 数据库接入的挑战与设计原则

### 1.1 Agent 接入数据库的四大独特挑战

AI Agent 接入企业数据库与传统 Web 应用有本质区别，面临四大独特挑战：

```mermaid
flowchart LR
    subgraph 挑战一_动态SQL
        C1A["Agent 根据自然语言<br/>动态生成 SQL"] --> C1B["SQL 结构不可预测<br/>传统预编译难以完全覆盖"]
        C1B --> C1C["注入风险 exponentially 上升"]
    end
    subgraph 挑战二_权限复杂
        C2A["Agent 代表用户执行<br/>但身份是服务账号"] --> C2B["需同时校验<br/>用户权限 + Agent 权限"]
        C2B --> C2C["传统单一身份模型失效"]
    end
    subgraph 挑战三_性能不可控
        C3A["LLM 生成的 SQL<br/>可能极低效（全表扫描）"] --> C3B["一条烂 SQL<br/>拖垮整个数据库"]
        C3B --> C3C["影响线上业务系统"]
    end
    subgraph 挑战四_审计溯源
        C4A["Agent 自动执行<br/>无人实时监督"] --> C4B["出问题需快速定位<br/>谁授权 + 为什么执行"]
        C4B --> C4C["审计粒度要求极高"]
    end

    C1C & C2C & C3C & C4C --> SOLUTION["五层接入架构<br/>+ 五重防注入<br/>+ 三层认证<br/>+ 全链路审计"]
    style SOLUTION fill:#50b83c,color:#fff
```

### 1.2 八大设计原则

| 原则 | 含义 | 落地措施 |
|:----|:-----|:--------|
| **P1 最小权限** | Agent 数据库账号只授予完成任务所需的最小权限 | 只读账号 + 白名单表 + 禁止 DDL |
| **P2 纵深防御** | 不依赖单一防护，多层叠加 | 参数化 + 白名单 + 语义检测 + 审计 |
| **P3 参数化优先** | 永远不拼接 SQL 字符串 | 强制 ORM / Prepared Statement |
| **P4 失败安全** | 异常时默认拒绝而非放行 | 白名单模式：未明确允许即拒绝 |
| **P5 可观测性** | 每条 SQL 可追溯 | Trace ID + 审计日志 + 慢查询监控 |
| **P6 资源隔离** | Agent 不影响业务系统 | 独立连接池 + 独立只读副本 + 限流 |
| **P7 多库适配** | 一套代码适配多种数据库 | 方言抽象层 + ORM 屏蔽差异 |
| **P8 可测试性** | 安全措施可验证 | 注入测试集 + 性能基准 + 容灾演练 |

### 1.3 五层接入架构总览

```mermaid
graph TB
    subgraph L5_监控层["L5 监控与审计层"]
        M1[慢查询监控<br/>Prometheus + Grafana]
        M2[审计日志<br/>ELK 全量 SQL 记录]
        M3[异常告警<br/>钉钉/邮件实时告警]
    end

    subgraph L4_访问层["L4 数据访问层（DAO/Repository）"]
        D1[只读 DAO<br/>查询服务]
        D2[读写 DAO<br/>受控写入]
        D3[批量 DAO<br/>批量操作]
        D4[事务管理<br/>声明式事务]
    end

    subgraph L3_安全层["L3 安全防护层"]
        S1[SQL 注入检测<br/>五重防护]
        S2[权限校验<br/>RBAC + ABAC]
        S3[脱敏过滤<br/>字段级 PII 脱敏]
        S4[限流配额<br/>QPS + 数据量限制]
    end

    subgraph L2_连接池层["L2 连接池层"]
        P1[HikariCP / SQLAlchemy Pool]
        P2[连接泄漏检测]
        P3[健康检查 + 自动回收]
        P4[读写分离路由]
    end

    subgraph L1_适配层["L1 多数据库适配层"]
        A1[MySQL 方言]
        A2[PostgreSQL 方言]
        A3[Oracle 方言]
        A4[SQL Server 方言]
        A5[方言抽象接口]
    end

    subgraph DB["企业数据库集群"]
        DB1[(MySQL 主从)]
        DB2[(PostgreSQL)]
        DB3[(Oracle)]
        DB4[(SQL Server)]
    end

    Agent["AI Agent 服务"] --> L4
    L4 --> L3 --> L2 --> L1 --> DB
    L5 -.监控.-> L4 & L3 & L2 & L1

    style L3 fill:#f5222d,color:#fff
    style L2 fill:#1890ff,color:#fff
    style L1 fill:#52c41a,color:#fff
```

---

## 二、数据库连接方式选型

### 2.1 三种连接方式对比（JDBC / ODBC / ORM）

| 维度 | JDBC（Java 原生） | ODBC（跨平台底层） | ORM（对象关系映射） |
|:----|:-----------------|:------------------|:------------------|
| **抽象层级** | 底层 API | 底层 API | 高层抽象 |
| **开发效率** | 低（手写 SQL + ResultSet） | 低（C API，Java 用 JDBC-ODBC 桥） | 高（对象操作，自动生成 SQL） |
| **SQL 注入防护** | 手动 Prepared Statement | 手动参数绑定 | 内置参数化，默认安全 |
| **多数据库适配** | 需手动切换 Driver | 天然跨平台但性能差 | 方言自动适配 |
| **性能** | 最高（零开销） | 低（额外桥接层） | 中（有 ORM 开销 5-15%） |
| **可维护性** | 低（SQL 硬编码） | 低 | 高（代码与 SQL 解耦） |
| **缓存支持** | 无 | 无 | 内置二级缓存 |
| **适用场景** | 极致性能场景 | 遗留系统兼容 | **Agent 项目首选** |

### 2.2 ORM 框架选型决策矩阵

| ORM 框架 | 语言 | 多库适配 | 异步支持 | 性能 | 社区活跃度 | Agent 适用性 |
|:--------|:-----|:--------|:--------|:-----|:----------|:-----------|
| **SQLAlchemy** | Python | ★★★★★ | ★★★★★（asyncio） | ★★★★ | ★★★★★ | **首选**（Python AI 生态） |
| **MyBatis** | Java | ★★★★ | ★★★（需插件） | ★★★★★ | ★★★★★ | **首选**（Java 企业生态） |
| Django ORM | Python | ★★★ | ★★ | ★★★ | ★★★★ | 不推荐（绑定 Django） |
| Hibernate | Java | ★★★★★ | ★★★ | ★★★ | ★★★★ | 可选（重量级） |
| SQLModel | Python | ★★★★ | ★★★★ | ★★★★ | ★★★ | 可选（基于 SQLAlchemy） |

### 2.3 选型推荐与理由

```mermaid
flowchart LR
    subgraph Python_AI服务["Python AI 服务（推荐 SQLAlchemy）"]
        R1["理由1: AI 生态原生支持<br/>LangChain/LlamaIndex 均基于 SQLAlchemy"]
        R2["理由2: 异步支持完善<br/>async SQLAlchemy + asyncpg/aiomysql"]
        R3["理由3: Core + ORM 双层<br/>Core 做复杂查询，ORM 做对象映射"]
        R4["理由4: 方言系统成熟<br/>20+ 数据库方言开箱即用"]
    end
    subgraph Java_业务服务["Java 业务服务（推荐 MyBatis + HikariCP）"]
        J1["理由1: SQL 可控性高<br/>XML/注解中 SQL 可审计"]
        J2["理由2: HikariCP 性能最强<br/>Spring Boot 默认连接池"]
        J3["理由3: 企业生态成熟<br/>与 Spring Security/事务无缝集成"]
        J4["理由4: MyBatis-Plus 增强<br/>分页/逻辑删除/自动填充"]
    end

    style R1 fill:#52c41a,color:#fff
    style J1 fill:#1890ff,color:#fff
```

> **最终选型**：Python 端用 **SQLAlchemy 2.0（async） + asyncpg/aiomysql**，Java 端用 **MyBatis-Plus + HikariCP**。下文双语言给出完整实现。

---

## 三、身份认证与权限控制机制

### 3.1 三层身份认证体系

```mermaid
flowchart TB
    subgraph Layer1_应用层认证["Layer 1: 应用层（Agent 服务）"]
        L1A["用户 SSO 登录<br/>获取 JWT Token"]
        L1B["JWT 解析用户身份<br/>user_id / roles / dept"]
        L1C["RBAC + ABAC 策略引擎<br/>校验用户是否有权执行此操作"]
    end

    subgraph Layer2_数据库层认证["Layer 2: 数据库层（账号隔离）"]
        L2A["Agent 服务账号<br/>agent_reader（只读）"]
        L2B["Agent 服务账号<br/>agent_writer（受限写）"]
        L2C["按操作类型路由账号<br/>查询→reader, 写入→writer"]
        L2D["数据库层 GRANT 权限<br/>仅白名单表 SELECT/INSERT"]
    end

    subgraph Layer3_数据层认证["Layer 3: 数据层（行级/列级）"]
        L3A["行级权限<br/>WHERE dept_id = 用户部门"]
        L3B["列级权限<br/>PII 字段脱敏返回"]
        L3C["数据范围过滤<br/>只查自己有权的数据行"]
    end

    L1A --> L1B --> L1C
    L1C --> L2C --> L2A & L2B
    L2A & L2B --> L2D
    L2D --> L3A & L3B & L3C

    style L1C fill:#f5222d,color:#fff
    style L2D fill:#fa8c16,color:#fff
    style L3C fill:#722ed1,color:#fff
```

### 3.2 应用层 RBAC + ABAC 权限模型

| 权限模型 | 控制维度 | 示例 | 实现方式 |
|:--------|:--------|:-----|:--------|
| **RBAC**（基于角色） | 角色 → 操作 | `admin` 可写，`user` 只读 | 角色表 + 权限表 + 角色权限关联表 |
| **ABAC**（基于属性） | 用户属性 + 资源属性 + 环境 | 用户部门 = 数据部门 且 时间 = 工作时间 | 策略引擎（如 OPA/Cedar） |
| **行级权限** | 数据行级别 | 只能查本部门数据 | SQL 自动注入 `WHERE dept_id = :user_dept` |
| **列级权限** | 字段级别 | 手机号脱敏为 `138****5678` | 查询后脱敏 / 数据库视图 |

**RBAC 权限矩阵示例**：

| 角色 | 查询知识库 | 查询业务数据 | 写入数据 | 管理配置 | 查看审计 |
|:-----|:----------|:-----------|:--------|:--------|:--------|
| `agent_admin` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `agent_editor` | ✓ | ✓ | ✓ | ✗ | ✓（自己） |
| `agent_user` | ✓ | ✓（受限） | ✗ | ✗ | ✗ |
| `agent_guest` | ✓（公开） | ✗ | ✗ | ✗ | ✗ |

### 3.3 数据库层账号隔离策略

**核心原则**：Agent 不使用业务系统的数据库账号，而是创建**专属受限账号**。

```sql
-- MySQL 示例：创建 Agent 专属只读账号
CREATE USER 'agent_reader'@'10.%' IDENTIFIED BY 'STRONG_PASSWORD_HERE'
    REQUIRE SSL  -- 强制 SSL 连接
    WITH MAX_QUERIES_PER_HOUR 1000   -- 每小时最多 1000 次查询
         MAX_CONNECTIONS_PER_HOUR 50; -- 每小时最多 50 个连接

-- 仅授予白名单表的 SELECT 权限
GRANT SELECT ON knowledge_db.documents TO 'agent_reader'@'10.%';
GRANT SELECT ON knowledge_db.doc_chunks TO 'agent_reader'@'10.%';
GRANT SELECT ON business_db.products TO 'agent_reader'@'10.%';
GRANT SELECT ON business_db.orders_summary TO 'agent_reader'@'10.%';  -- 只读汇总视图

-- 显式禁止危险操作
REVOKE ALL PRIVILEGES ON *.* FROM 'agent_reader'@'10.%';
-- 禁止访问系统表、用户表、密码表
REVOKE SELECT ON mysql.* FROM 'agent_reader'@'10.%';
REVOKE SELECT ON information_schema.schemata FROM 'agent_reader'@'10.%';

-- 创建受限写账号（仅允许写入审计表和反馈表）
CREATE USER 'agent_writer'@'10.%' IDENTIFIED BY 'STRONG_PASSWORD_HERE' REQUIRE SSL;
GRANT INSERT ON knowledge_db.query_logs TO 'agent_writer'@'10.%';
GRANT INSERT ON knowledge_db.user_feedback TO 'agent_writer'@'10.%';
-- 禁止 UPDATE/DELETE（审计日志只追加不修改）
```

### 3.4 数据层行级与列级权限控制

```python
# 行级权限：自动注入 WHERE 条件（Python SQLAlchemy 示例）
from sqlalchemy import event, select
from sqlalchemy.orm import Session

class RowLevelSecurityListener:
    """
    自动在所有查询中注入行级权限过滤条件。
    效果：用户只能查到自己部门的数据，无需在每个查询中手写 WHERE。
    """

    @event.listens_for(Session, "do_orm_execute")
    def _apply_row_filter(execute_state):
        if not execute_state.is_select:
            return
        user = execute_state.execution_options.get("current_user")
        if not user:
            return
        # 对 Document 模型自动注入 dept_id 过滤
        if execute_state.is_orm_statement and "Document" in str(execute_state.statement):
            execute_state.statement = execute_state.statement.where(
                Document.dept_id.in_(user.accessible_depts)
            )


# 列级权限：PII 字段自动脱敏
class ColumnLevelDesensitizer:
    """查询结果返回前，对 PII 字段自动脱敏。"""

    PII_RULES = {
        "phone": lambda v: v[:3] + "****" + v[-4:] if v and len(v) >= 7 else v,
        "id_card": lambda v: v[:6] + "********" + v[-4:] if v and len(v) >= 14 else v,
        "email": lambda v: v[:2] + "***@" + v.split("@")[-1] if v and "@" in v else v,
        "bank_card": lambda v: v[:4] + "***********" + v[-4:] if v and len(v) >= 12 else v,
    }

    def desensitize(self, row: dict, user_role: str) -> dict:
        """根据用户角色决定是否脱敏。admin 不脱敏，普通用户脱敏。"""
        if user_role == "agent_admin":
            return row  # 管理员看明文
        for field, rule in self.PII_RULES.items():
            if field in row and row[field]:
                row[field] = rule(str(row[field]))
        return row
```

---

## 四、数据访问策略

### 4.1 读写分离架构

```mermaid
flowchart LR
    Agent["Agent 服务"] --> Router{"读写路由器"}

    Router -->|"SELECT 查询"| RO["只读副本<br/>agent_reader 账号"]
    Router -->|"INSERT/UPDATE"| RW["主库<br/>agent_writer 账号"]
    Router -->|"复杂分析"| OLAP["OLAP 只读节点<br/>专用分析账号"]

    RO --> RO1[(MySQL Slave 1)]
    RO --> RO2[(MySQL Slave 2)]
    RW --> RW1[(MySQL Master)]
    OLAP --> OLAP1[(ClickHouse / 只读 PG)]

    style Router fill:#722ed1,color:#fff
```

```python
# Python 读写分离路由实现
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

class ReadWriteSplitRouter:
    """
    根据 SQL 类型自动路由到主库或只读副本。
    SELECT → 只读副本（轮询负载均衡）
    INSERT/UPDATE/DELETE → 主库
    """

    def __init__(self, master_url: str, slave_urls: list):
        self.master = create_engine(master_url, pool_size=10, max_overflow=20)
        self.slaves = [create_engine(url, pool_size=10, max_overflow=20)
                       for url in slave_urls]
        self._slave_idx = 0

    def get_engine(self, is_write: bool = False):
        if is_write:
            return self.master
        # 轮询选择从库
        engine = self.slaves[self._slave_idx % len(self.slaves)]
        self._slave_idx += 1
        return engine

    @contextmanager
    def session(self, is_write: bool = False) -> Session:
        engine = self.get_engine(is_write)
        session = sessionmaker(bind=engine)()
        try:
            yield session
            if is_write:
                session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
```

### 4.2 多租户数据隔离

| 隔离策略 | 实现 | 适用场景 | 优缺点 |
|:--------|:-----|:--------|:------|
| **独立数据库** | 每个租户一个数据库 | 强合规需求（金融/医疗） | 最安全但成本最高 |
| **共享数据库独立 Schema** | 同库不同 Schema | 中等规模 | 较安全，迁移较难 |
| **共享表 + 租户字段** | 每行带 `tenant_id` | **Agent 推荐** | 成本低，需严格过滤 |

```python
# 共享表 + tenant_id 自动过滤
class TenantFilter:
    """所有查询自动注入 tenant_id 过滤，防止跨租户数据泄露。"""

    @event.listens_for(Session, "do_orm_execute")
    def _filter_tenant(execute_state):
        if not execute_state.is_select:
            return
        tenant_id = execute_state.execution_options.get("tenant_id")
        if tenant_id is None:
            return
        # 对所有带 tenant_id 的模型自动过滤
        for desc in execute_state.bind_mapper.entities:
            if hasattr(desc.entity, "tenant_id"):
                execute_state.statement = execute_state.statement.where(
                    desc.entity.tenant_id == tenant_id
                )
```

### 4.3 只读视图与白名单表策略

**白名单表策略**：Agent 只能访问显式允许的表/视图，其余全部拒绝。

```python
# 白名单配置（YAML）
"""
# agent_db_whitelist.yaml
allowed_tables:
  knowledge_db:
    - documents          # 文档表
    - doc_chunks         # 文档切片表
    - doc_categories     # 文档分类
  business_db:
    - products            # 产品表（只读）
    - orders_summary      # 订单汇总视图（只读，非原表）
    - customer_public     # 客户公开信息视图（已脱敏）

forbidden_tables:
  - mysql.user            # 数据库用户表
  - business_db.orders    # 订单原表（只能看汇总视图）
  - business_db.customer  # 客户原表（含 PII，只能看脱敏视图）

max_rows_per_query: 10000   # 单次查询最多返回 10000 行
max_query_timeout_sec: 30   # 查询超时 30 秒
"""
```

### 4.4 字段级脱敏与数据最小化

**数据最小化原则**：Agent 查询只取必要字段，禁止 `SELECT *`。

```python
from sqlalchemy import select
from typing import List

class SafeQueryExecutor:
    """强制字段级数据最小化 + PII 脱敏。"""

    # 字段权限配置：哪些角色能看到哪些字段
    FIELD_PERMISSIONS = {
        "customer": {
            "agent_admin": ["id", "name", "phone", "email", "address", "credit_limit"],
            "agent_user":  ["id", "name", "phone_masked", "email_masked"],  # 不含地址/额度
            "agent_guest": ["id", "name"],  # 只能看到名字
        }
    }

    def safe_select(self, model, user_role: str, conditions: dict, limit: int = 100):
        """根据角色选择允许的字段，自动排除无权字段。"""
        allowed_fields = self.FIELD_PERMISSIONS.get(model.__tablename__, {}).get(user_role, [])
        if not allowed_fields:
            raise PermissionError(f"角色 {user_role} 无权访问表 {model.__tablename__}")

        # 构建只含允许字段的查询
        columns = [getattr(model, f) for f in allowed_fields if hasattr(model, f)]
        stmt = select(*columns).limit(min(limit, 10000))  # 强制上限

        # 添加条件
        for key, value in conditions.items():
            if hasattr(model, key):
                stmt = stmt.where(getattr(model, key) == value)

        return stmt
```

### 4.5 限流配额与资源隔离

| 限流维度 | 阈值 | 实现 | 目的 |
|:--------|:-----|:-----|:-----|
| **QPS 限制** | Agent 服务 ≤ 50 QPS | 令牌桶（Redis + Lua） | 防止 Agent 压垮数据库 |
| **数据量限制** | 单次查询 ≤ 10000 行 | SQL LIMIT 强制注入 | 防止大结果集拖垮内存 |
| **超时限制** | 查询 ≤ 30 秒 | 数据库 `statement_timeout` | 防止慢查询占连接 |
| **并发限制** | Agent 连接池 ≤ 20 | 连接池容量限制 | 资源隔离 |
| **时间窗口** | 非工作时间降级 | ABAC 时间策略 | 保护业务高峰期 |

---

## 五、SQL 注入防护措施

### 5.1 五重防护体系总览

```mermaid
flowchart LR
    INPUT["用户自然语言输入"] --> LLM["LLM 生成 SQL"]

    LLM --> G1{"第一重<br/>参数化查询"}
    G1 -->|"已参数化"| G2{"第二重<br/>输入校验 + 白名单"}
    G1 -->|"未参数化<br/>（拼接SQL）"| BLOCK1["❌ 拒绝执行"]
    G2 -->|"校验通过"| G3{"第三重<br/>SQL 语义检测"}
    G2 -->|"含危险字符"| BLOCK2["❌ 拒绝 + 告警"]
    G3 -->|"语义安全"| G4{"第四重<br/>LLM SQL 安全校验"}
    G3 -->|"含危险语义"| BLOCK3["❌ 拒绝 + 告警"]
    G4 -->|"安全"| G5{"第五重<br/>执行 + 审计"}
    G4 -->|"不安全"| BLOCK4["❌ 拒绝 + 告警"]
    G5 -->|"执行成功"| AUDIT["审计日志记录"]
    G5 -->|"执行异常"| ERROR["异常处理 + 告警"]

    style BLOCK1 fill:#f5222d,color:#fff
    style BLOCK2 fill:#f5222d,color:#fff
    style BLOCK3 fill:#f5222d,color:#fff
    style BLOCK4 fill:#f5222d,color:#fff
    style AUDIT fill:#52c41a,color:#fff
```

### 5.2 第一重：参数化查询（必选）

**核心原则**：永远不拼接 SQL 字符串，所有变量必须通过参数传递。

```python
# ✅ 正确：参数化查询（安全）
from sqlalchemy import text

stmt = text("SELECT * FROM documents WHERE title LIKE :keyword AND dept_id = :dept_id")
result = session.execute(stmt, {"keyword": f"%{user_input}%", "dept_id": user_dept})

# ❌ 错误：字符串拼接（SQL 注入漏洞！）
# stmt = f"SELECT * FROM documents WHERE title LIKE '%{user_input}%'"
# result = session.execute(stmt)
```

```java
// ✅ 正确：MyBatis 参数化（安全）
// Mapper XML
// <select id="searchDocs" resultType="Document">
//   SELECT * FROM documents WHERE title LIKE #{keyword} AND dept_id = #{deptId}
// </select>

// ❌ 错误：${} 拼接（SQL 注入漏洞！）
// <select id="searchDocs" resultType="Document">
//   SELECT * FROM documents WHERE title LIKE '%${keyword}%'
// </select>
```

### 5.3 第二重：输入校验与白名单

```python
import re
from typing import Optional

class InputValidator:
    """对用户输入和 LLM 生成的 SQL 参数进行严格校验。"""

    # 白名单字符：只允许字母、数字、中文、空格、基本标点
    ALLOWED_PATTERN = re.compile(r'^[\u4e00-\u9fa5a-zA-Z0-9\s\-_.,()（）【】]+$')

    # 黑名单关键词（SQL 注入常见特征）
    SQL_INJECTION_PATTERNS = [
        r"(?i)(union\s+select)",       # UNION 注入
        r"(?i)(;\s*drop\s+table)",     # 删表
        r"(?i)(;\s*delete\s+from)",    # 删数据
        r"(?i)(--|/\*|\*/)",           # SQL 注释
        r"(?i)(xp_cmdshell|sp_executesql)",  # 存储过程执行
        r"(?i)(information_schema)",   # 系统表探测
        r"(?i)(benchmark\s*\(|sleep\s*\()",  # 时间盲注
    ]

    @classmethod
    def validate(cls, user_input: str, max_length: int = 500) -> Optional[str]:
        """校验用户输入，返回清洗后的值或 None（表示不合法）。"""
        if not user_input or len(user_input) > max_length:
            return None

        # 检查黑名单
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, user_input):
                # 记录攻击尝试
                SecurityAuditLog.record(
                    event="sql_injection_attempt",
                    input=user_input,
                    pattern=pattern
                )
                return None

        # 白名单字符检查（允许的字符集）
        if not cls.ALLOWED_PATTERN.match(user_input):
            return None

        return user_input.strip()

    @classmethod
    def validate_table_name(cls, table_name: str, allowed_tables: set) -> bool:
        """表名必须严格在白名单中，防止 LLM 生成访问非授权表的 SQL。"""
        return table_name.lower() in {t.lower() for t in allowed_tables}
```

### 5.4 第三重：SQL 语义安全检测

```python
import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML

class SQLSemanticChecker:
    """
    解析 SQL 语句结构，检测危险语义：
    - 只允许 SELECT，禁止 INSERT/UPDATE/DELETE/DDL（除非显式授权写操作）
    - 检查访问的表是否在白名单
    - 检查是否有子查询访问系统表
    - 检查是否有 INTO OUTFILE（文件导出攻击）
    """

    DANGEROUS_KEYWORDS = {
        'INTO OUTFILE', 'INTO DUMPFILE',   # 文件导出
        'LOAD_FILE',                        # 文件读取
        'BENCHMARK', 'SLEEP',              # 时间盲注
        'XP_CMDSHELL',                     # 命令执行
    }

    ALLOWED_DML = {'SELECT'}  # 默认只允许 SELECT

    @classmethod
    def check(cls, sql: str, allowed_tables: set, allow_write: bool = False) -> dict:
        """返回 {"safe": bool, "reasons": list}"""
        reasons = []
        parsed = sqlparse.parse(sql)
        if not parsed:
            return {"safe": False, "reasons": ["SQL 解析失败"]}

        for stmt in parsed:
            stmt_str = str(stmt).upper()

            # 1. 检查 DML 类型
            dml_type = cls._get_dml_type(stmt)
            allowed = cls.ALLOWED_DML | ({'INSERT', 'UPDATE', 'DELETE'} if allow_write else set())
            if dml_type not in allowed:
                reasons.append(f"不允许的 DML 操作: {dml_type}")

            # 2. 检查危险关键词
            for kw in cls.DANGEROUS_KEYWORDS:
                if kw in stmt_str:
                    reasons.append(f"检测到危险关键词: {kw}")

            # 3. 检查访问的表是否在白名单
            tables = cls._extract_tables(stmt)
            for t in tables:
                if t.lower() not in {at.lower() for at in allowed_tables}:
                    reasons.append(f"访问非白名单表: {t}")

        return {"safe": len(reasons) == 0, "reasons": reasons}

    @classmethod
    def _get_dml_type(cls, stmt) -> str:
        for token in stmt.tokens:
            if token.ttype is DML:
                return token.value.upper()
        return "UNKNOWN"

    @classmethod
    def _extract_tables(cls, stmt) -> list:
        tables = []
        for token in stmt.tokens:
            if isinstance(token, IdentifierList):
                for identifier in token.get_identifiers():
                    tables.append(str(identifier))
            elif isinstance(token, Identifier):
                tables.append(str(token))
        return tables
```

### 5.5 第四重：LLM 生成 SQL 的安全约束

当 Agent 用 LLM 将自然语言转为 SQL（Text-to-SQL）时，需额外约束：

```python
class LLMSQLSafetyGuard:
    """
    LLM 生成的 SQL 必须经过额外的安全约束：
    1. Prompt 中强制注入"只能查询白名单表"指令
    2. LLM 输出的 SQL 经 sqlparse 解析 + 语义检测
    3. 在沙箱数据库（只读副本的副本）先试跑 EXPLAIN
    4. 试跑通过后再在正式库执行
    """

    SYSTEM_PROMPT = """你是一个 SQL 生成助手。严格遵守以下规则：
    1. 只能生成 SELECT 语句，禁止 INSERT/UPDATE/DELETE/DROP
    2. 只能查询以下白名单表: {allowed_tables}
    3. 必须使用参数化查询占位符，不要拼接用户输入
    4. 必须添加 LIMIT 子句，最大返回 1000 行
    5. 禁止访问系统表（information_schema/mysql/pg_catalog）
    6. 禁止使用 INTO OUTFILE / LOAD_FILE / BENCHMARK / SLEEP
    7. 如果用户请求超出白名单范围，返回 "REFUSED: 原因"

    用户问题: {user_question}
    可用表结构: {table_schemas}
    """

    def generate_and_validate(self, user_question: str, allowed_tables: set,
                              table_schemas: dict) -> dict:
        # Step 1: LLM 生成 SQL
        prompt = self.SYSTEM_PROMPT.format(
            allowed_tables=allowed_tables,
            user_question=user_question,
            table_schemas=table_schemas
        )
        raw_sql = self.llm.generate(prompt)

        if raw_sql.startswith("REFUSED"):
            return {"status": "refused", "reason": raw_sql}

        # Step 2: 语义安全检测（第三重）
        check_result = SQLSemanticChecker.check(raw_sql, allowed_tables, allow_write=False)
        if not check_result["safe"]:
            return {"status": "blocked", "reasons": check_result["reasons"]}

        # Step 3: 沙箱 EXPLAIN 验证（检查执行计划是否合理）
        explain_result = self._sandbox_explain(raw_sql)
        if explain_result.get("full_table_scan"):
            return {"status": "blocked", "reason": "检测到全表扫描，拒绝执行"}

        # Step 4: 返回安全 SQL
        return {"status": "safe", "sql": raw_sql}
```

### 5.6 第五重：审计回溯与实时告警

```python
import time, hashlib, json
from datetime import datetime

class SQLAuditLogger:
    """
    全量 SQL 审计日志，满足合规要求：
    - 谁（user_id）+ 何时（timestamp）+ 通过谁（agent_id）
    - 执行了什么 SQL（完整 SQL + 参数）
    - 访问了什么表
    - 执行结果（成功/失败 + 影响行数 + 耗时）
    - 不可篡改（链式哈希）
    """

    def __init__(self, audit_db_engine):
        self.engine = audit_db_engine
        self._last_hash = "GENESIS"

    def log(self, user_id: str, agent_id: str, sql: str, params: dict,
            tables: list, result: str, affected_rows: int, latency_ms: float,
            trace_id: str):
        # 链式哈希（防篡改）
        record = {
            "ts": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "agent_id": agent_id,
            "sql": sql,
            "params": json.dumps(params, ensure_ascii=False),
            "tables": json.dumps(tables),
            "result": result,  # success / error / blocked
            "affected_rows": affected_rows,
            "latency_ms": latency_ms,
            "trace_id": trace_id,
            "prev_hash": self._last_hash,
        }
        record["hash"] = hashlib.sha256(
            json.dumps(record, sort_keys=True).encode()
        ).hexdigest()
        self._last_hash = record["hash"]

        # 写入审计库（WORM 存储：只追加不修改）
        self.engine.execute(
            "INSERT INTO sql_audit_log VALUES (:ts, :user_id, :agent_id, :sql, "
            ":params, :tables, :result, :affected_rows, :latency_ms, :trace_id, :hash)",
            record
        )

        # 高危操作实时告警
        if result == "blocked" or affected_rows > 1000:
            self._alert(record)
```

---

## 六、连接池配置与调优

### 6.1 连接池核心参数详解

| 参数 | 含义 | 推荐值 | 调优依据 |
|:----|:-----|:------|:--------|
| `maximumPoolSize` | 最大连接数 | 20 | `(核心数 × 2 + 有效磁盘数)` 或按 QPS ÷ 单连接吞吐计算 |
| `minimumIdle` | 最小空闲连接 | 10 | 与最大连接数相同（避免频繁创建销毁） |
| `connectionTimeout` | 获取连接超时 | 30000ms | 应用可容忍的等待上限 |
| `idleTimeout` | 空闲连接超时 | 600000ms（10min） | 空闲超过此值则回收 |
| `maxLifetime` | 连接最大生命周期 | 1800000ms（30min） | 防止长时间使用导致连接老化 |
| `leakDetectionThreshold` | 泄漏检测阈值 | 60000ms（60s） | 超过此时间未归还则告警泄漏 |
| `connectionTestQuery` | 连接有效性检查 | `SELECT 1` | 轻量级心跳查询 |

### 6.2 HikariCP 配置（Java 推荐）

```yaml
# application.yml（Spring Boot + HikariCP 完整配置）
spring:
  datasource:
    # 主库（读写）
    master:
      jdbc-url: jdbc:postgresql://10.0.1.10:5432/business_db?sslmode=require
      username: agent_writer
      password: ${DB_MASTER_PASSWORD}  # 从环境变量/Vault 读取，不硬编码
      driver-class-name: org.postgresql.Driver
      hikari:
        pool-name: AgentMasterPool
        maximum-pool-size: 10          # 写操作少，连接数小
        minimum-idle: 5
        connection-timeout: 30000
        idle-timeout: 600000
        max-lifetime: 1800000
        leak-detection-threshold: 60000
        connection-test-query: SELECT 1
        # 安全配置
        data-source-properties:
          ssl: true
          sslmode: verify-full
          sslrootcert: /etc/ssl/certs/db-ca.pem
          # 防止超时查询拖垮连接
          loginTimeout: 10
          socketTimeout: 60            # 单次查询 60s 超时
          cancelSignalTimeout: 10

    # 只读副本（读操作）
    slave:
      jdbc-url: jdbc:postgresql://10.0.1.20:5432/business_db?sslmode=require
      username: agent_reader
      password: ${DB_SLAVE_PASSWORD}
      driver-class-name: org.postgresql.Driver
      hikari:
        pool-name: AgentSlavePool
        maximum-pool-size: 20          # 读多，连接数大
        minimum-idle: 10
        connection-timeout: 30000
        idle-timeout: 600000
        max-lifetime: 1800000
        leak-detection-threshold: 60000
        connection-test-query: SELECT 1
        data-source-properties:
          ssl: true
          sslmode: verify-full
          socketTimeout: 30            # 读查询 30s 超时（更严格）
```

### 6.3 SQLAlchemy 连接池配置（Python 推荐）

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import AsyncAdaptedQueuePool

# 异步引擎配置（推荐生产使用）
engine = create_async_engine(
    "postgresql+asyncpg://agent_reader:${DB_PASSWORD}@10.0.1.20:5432/business_db",
    # 连接池配置
    poolclass=AsyncAdaptedQueuePool,
    pool_size=20,              # 连接池大小
    max_overflow=10,           # 超出 pool_size 的最大临时连接
    pool_timeout=30,           # 获取连接超时 30s
    pool_recycle=1800,         # 连接回收周期 30min
    pool_pre_ping=True,        # 使用前发 ping 检查连接有效性
    # 安全配置
    connect_args={
        "ssl": "require",                              # 强制 SSL
        "server_settings": {
            "statement_timeout": "30000",              # 查询超时 30s
            "lock_timeout": "5000",                    # 锁超时 5s
            "idle_in_transaction_session_timeout": "60000"  # 空闲事务超时 60s
        }
    },
    # 性能配置
    echo=False,                # 生产关闭 SQL 日志（用审计日志替代）
    echo_pool=False,           # 连接池日志
)

# 同步引擎配置（用于需要同步的场景）
sync_engine = create_engine(
    "postgresql+psycopg2://agent_reader:${DB_PASSWORD}@10.0.1.20:5432/business_db",
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    connect_args={"sslmode": "require", "connect_timeout": 10},
)
```

### 6.4 连接池容量计算公式

**PostgreSQL 官方推荐公式**：

```
连接数 = (核心数 × 2) + 有效磁盘数
```

**Agent 场景实用公式**：

```
pool_size = ceil(目标 QPS × 平均查询耗时(秒))
max_pool = pool_size × 1.5  （留 50% 余量应对突发）

示例：
- 目标 QPS = 50
- 平均查询耗时 = 0.1s
- pool_size = ceil(50 × 0.1) = 5
- max_pool = ceil(5 × 1.5) = 8

但考虑 AI 场景查询可能较慢（LLM 思考时间）：
- 实际查询耗时含 LLM 推理 = 2s
- pool_size = ceil(50 × 2) = 100 → 过大
- 折中：pool_size = 20，max_overflow = 10，配合排队
```

### 6.5 连接泄漏检测与容灾配置

```python
import logging
from sqlalchemy import event

LOG = logging.getLogger("DBPoolMonitor")

class ConnectionLeakDetector:
    """
    监控连接池状态，检测泄漏，自动告警。
    """

    @event.listens_for(engine.sync_engine, "checkout")
    def on_checkout(dbapi_conn, conn_record, conn_proxy):
        """连接被借出时记录"""
        conn_record.info["checkout_time"] = time.time()

    @event.listens_for(engine.sync_engine, "checkin")
    def on_checkin(dbapi_conn, conn_record):
        """连接归还时检查持有时间"""
        checkout_time = conn_record.info.get("checkout_time")
        if checkout_time:
            hold_time = time.time() - checkout_time
            if hold_time > 5.0:  # 持有超过 5 秒告警
                LOG.warning(
                    f"连接持有时间过长: {hold_time:.2f}s, "
                    f"可能存在泄漏。Trace: {conn_record.info.get('trace_id')}"
                )

    @staticmethod
    def pool_status() -> dict:
        """获取连接池实时状态"""
        pool = engine.sync_engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.status()  # 详细状态字符串
        }
```

---

## 七、异常处理机制

### 7.1 异常分级体系

| 等级 | 异常类型 | 示例 | 处理策略 | 告警 |
|:----|:--------|:-----|:--------|:----|
| **P0 致命** | 数据库不可达 | ConnectionRefusedError | 熔断 + 降级 + 立即告警 | 钉钉 + 电话 |
| **P0 致命** | 连接池耗尽 | PoolTimeoutException | 降级 + 告警 | 钉钉 |
| **P1 严重** | 查询超时 | TimeoutError | 重试 1 次 + 降级 | 钉钉 |
| **P1 严重** | 死锁 | DeadlockFound | 重试（退避） | 日志 |
| **P2 一般** | 唯一键冲突 | IntegrityError | 不重试 + 返回友好错误 | 日志 |
| **P2 一般** | 权限不足 | PermissionError | 不重试 + 审计 | 日志 + 审计 |
| **P3 轻微** | 空结果 | NoResultFound | 正常返回空 | 无 |

### 7.2 重试策略与退避算法

```python
import asyncio
import random
from functools import wraps
from typing import Type, Tuple, Callable

class RetryPolicy:
    """
    指数退避 + 抖动重试策略。
    适用于：网络抖动、死锁、临时不可达。
    不适用于：权限错误、SQL 语法错误、唯一键冲突。
    """

    # 可重试的异常
    RETRIABLE_EXCEPTIONS = (
        ConnectionError,
        TimeoutError,
        # psycopg2.OperationalError,  # 死锁/连接断开
        # asyncpg.ConnectionDoesNotExistError,
    )

    @classmethod
    def async_retry(cls, max_retries: int = 3,
                    base_delay: float = 0.5,
                    max_delay: float = 5.0,
                    retriable: Tuple[Type[Exception], ...] = None):
        """异步重试装饰器"""
        retriable = retriable or cls.RETRIABLE_EXCEPTIONS

        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                last_exception = None
                for attempt in range(max_retries + 1):
                    try:
                        return await func(*args, **kwargs)
                    except retriable as e:
                        last_exception = e
                        if attempt == max_retries:
                            break
                        # 指数退避 + 抖动
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        jitter = random.uniform(0, delay * 0.1)  # 10% 抖动
                        await asyncio.sleep(delay + jitter)
                        LOG.warning(f"重试 {attempt+1}/{max_retries}, "
                                   f"延迟 {delay:.2f}s, 异常: {e}")
                    except Exception as e:
                        # 不可重试异常，直接抛出
                        raise
                raise last_exception
            return wrapper
        return decorator
```

### 7.3 熔断降级机制

```python
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"      # 正常
    OPEN = "open"          # 熔断（拒绝所有请求）
    HALF_OPEN = "half_open"  # 半开（允许少量探测）

class CircuitBreaker:
    """
    数据库访问熔断器。
    当失败率超阈值时熔断，保护数据库不被持续冲击。
    """

    def __init__(self, failure_threshold: int = 10,
                 recovery_timeout: float = 60,
                 half_open_max_calls: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max = half_open_max_calls
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0
        self._half_open_calls = 0

    async def call(self, func, *args, **kwargs):
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
            else:
                raise CircuitBreakerOpenError("数据库熔断中，请求被拒绝")

        if self._state == CircuitState.HALF_OPEN and self._half_open_calls >= self.half_open_max:
            raise CircuitBreakerOpenError("半开状态探测次数已达上限")

        try:
            if self._state == CircuitState.HALF_OPEN:
                self._half_open_calls += 1
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self._failure_count = 0
        self._state = CircuitState.CLOSED

    def _on_failure(self):
        self._failure_count += 1
        self._last_failure_time = time.time()
        if self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            # 触发降级 + 告警
            LOG.error("数据库熔断器开启！")
```

### 7.4 异常处理代码实现

```python
from fastapi import HTTPException

class DatabaseExceptionHandler:
    """统一的数据库异常处理，转换为用户友好的错误响应。"""

    @staticmethod
    async def safe_execute(query_func, *args, **kwargs):
        try:
            return await query_func(*args, **kwargs)
        except ConnectionError as e:
            LOG.error(f"数据库连接失败: {e}")
            raise HTTPException(status_code=503, detail="服务暂时不可用，请稍后重试")
        except TimeoutError as e:
            LOG.error(f"查询超时: {e}")
            raise HTTPException(status_code=504, detail="查询超时，请简化问题后重试")
        except PermissionError as e:
            LOG.warning(f"权限不足: {e}")
            SecurityAuditLog.record(event="permission_denied", detail=str(e))
            raise HTTPException(status_code=403, detail="您无权访问此数据")
        except IntegrityError as e:
            LOG.warning(f"数据冲突: {e}")
            raise HTTPException(status_code=409, detail="数据已存在或冲突")
        except CircuitBreakerOpenError as e:
            LOG.error(f"熔断: {e}")
            # 降级：返回缓存或友好提示
            return {"degraded": True, "message": "系统繁忙，正在降级处理"}
        except Exception as e:
            LOG.error(f"未知数据库异常: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="内部错误，请联系管理员")
```

---

## 八、性能优化方案

### 8.1 数据库层面优化

| 优化项 | 措施 | 预期收益 |
|:------|:-----|:--------|
| **索引优化** | 为 Agent 高频查询字段建复合索引 | 查询延迟 -80% |
| **只读副本** | Agent 查询走独立只读副本 | 不影响主库业务 |
| **连接复用** | 连接池 + 长连接 | 连接创建开销 -90% |
| **查询超时** | `statement_timeout=30s` | 防止慢查询拖垮 |
| **结果集限制** | 强制 `LIMIT 10000` | 防止大结果集 OOM |

### 8.2 应用层面优化

```python
class QueryOptimizer:
    """应用层查询优化工具集。"""

    # 1. 批量查询替代循环单条查询
    @staticmethod
    async def batch_select(session, model, ids: list, batch_size=500):
        """批量查询，避免 N+1 问题。"""
        results = []
        for i in range(0, len(ids), batch_size):
            batch = ids[i:i+batch_size]
            stmt = select(model).where(model.id.in_(batch))
            results.extend(await session.execute(stmt))
        return results

    # 2. 只查必要字段（禁止 SELECT *）
    @staticmethod
    def select_fields(session, model, fields: list, conditions: dict):
        """只查指定字段，减少数据传输。"""
        columns = [getattr(model, f) for f in fields]
        stmt = select(*columns)
        for k, v in conditions.items():
            stmt = stmt.where(getattr(model, k) == v)
        return stmt

    # 3. 游标分页（深翻页优化）
    @staticmethod
    def cursor_pagination(session, model, last_id: int = 0, limit: int = 20):
        """
        游标分页替代 OFFSET：
        OFFSET 10000 性能极差（需扫描前 10000 行）
        WHERE id > last_id 性能恒定（走索引）
        """
        return select(model).where(model.id > last_id).order_by(model.id).limit(limit)
```

### 8.3 缓存策略

```mermaid
flowchart LR
    Q["Agent 查询请求"] --> C1{"L1 内存缓存<br/>命中?"}
    C1 -->|"命中"| R1["返回（<1ms）"]
    C1 -->|"未命中"| C2{"L2 Redis 缓存<br/>命中?"}
    C2 -->|"命中"| R2["返回 + 回填 L1（<5ms）"]
    C2 -->|"未命中"| DB["查询数据库"]
    DB --> C3{"结果可缓存?"}
    C3 -->|"是"| W["写入 L2 + L1<br/>TTL=300s"]
    C3 -->|"否"| R3["直接返回"]
    W --> R3

    style R1 fill:#52c41a,color:#fff
    style R2 fill:#1890ff,color:#fff
    style DB fill:#fa8c16,color:#fff
```

```python
import hashlib, json
from functools import wraps

class QueryCache:
    """三级缓存：内存 → Redis → 数据库。"""

    def __init__(self, redis_client, memory_cache_size=1000):
        self.redis = redis_client
        self.memory = {}  # L1
        self.memory_size = memory_cache_size

    def cached(self, ttl: int = 300, key_prefix: str = "agent_query"):
        """查询缓存装饰器。只有 SELECT 且非实时数据才缓存。"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # 生成缓存 Key
                cache_key = self._make_key(key_prefix, args, kwargs)

                # L1 内存
                if cache_key in self.memory:
                    return self.memory[cache_key]

                # L2 Redis
                redis_val = await self.redis.get(cache_key)
                if redis_val:
                    result = json.loads(redis_val)
                    self._set_memory(cache_key, result)
                    return result

                # 未命中，查数据库
                result = await func(*args, **kwargs)

                # 可缓存的数据写入缓存（实时数据不缓存）
                if kwargs.get("cacheable", True) and result is not None:
                    await self.redis.setex(cache_key, ttl, json.dumps(result, ensure_ascii=False))
                    self._set_memory(cache_key, result)

                return result
            return wrapper
        return decorator

    def _make_key(self, prefix, args, kwargs):
        """根据查询参数生成唯一 Key"""
        key_data = json.dumps({"args": str(args), "kwargs": kwargs}, sort_keys=True)
        return f"{prefix}:{hashlib.md5(key_data.encode()).hexdigest()}"

    def _set_memory(self, key, value):
        """L1 内存缓存（LRU 淘汰）"""
        if len(self.memory) >= self.memory_size:
            self.memory.pop(next(iter(self.memory)))  # 简单 FIFO
        self.memory[key] = value
```

### 8.4 慢查询治理

```python
class SlowQueryMonitor:
    """
    慢查询监控：超过阈值的查询自动记录 + 分析 + 告警。
    """

    SLOW_THRESHOLD_MS = 1000  # 1 秒以上为慢查询

    @event.listens_for(engine.sync_engine, "before_cursor_execute")
    def before_execute(conn, cursor, statement, parameters, context, executemany):
        context._query_start_time = time.time()

    @event.listens_for(engine.sync_engine, "after_cursor_execute")
    def after_execute(conn, cursor, statement, parameters, context, executemany):
        duration_ms = (time.time() - context._query_start_time) * 1000
        if duration_ms > self.SLOW_THRESHOLD_MS:
            # 记录慢查询
            SlowQueryLog.record(
                sql=statement,
                params=str(parameters),
                duration_ms=duration_ms,
                trace_id=context.execution_options.get("trace_id")
            )
            # 自动 EXPLAIN 分析
            explain = conn.execute(f"EXPLAIN ANALYZE {statement}", parameters)
            LOG.warning(f"慢查询 ({duration_ms:.0f}ms): {statement[:200]}...")
```

---

## 九、多数据库适配层设计

### 9.1 方言适配架构

```mermaid
flowchart TB
    APP["Agent 应用代码<br/>（使用统一接口）"] --> API["DatabaseAdapter 抽象接口"]

    API --> A1["MySQLAdapter"]
    API --> A2["PostgreSQLAdapter"]
    API --> A3["OracleAdapter"]
    API --> A4["SQLServerAdapter"]

    A1 --> D1[("MySQL")]
    A2 --> D2[("PostgreSQL")]
    A3 --> D3[("Oracle")]
    A4 --> D4[("SQL Server")]

    A1 & A2 & A3 & A4 --> COMMON["公共能力<br/>- 分页适配<br/>- 类型映射<br/>- 函数适配<br/>- 连接管理"]

    style API fill:#722ed1,color:#fff
    style COMMON fill:#52c41a,color:#fff
```

### 9.2 四种数据库方言差异对照表

| 特性 | MySQL | PostgreSQL | Oracle | SQL Server |
|:----|:------|:----------|:-------|:-----------|
| **分页** | `LIMIT 10 OFFSET 20` | `LIMIT 10 OFFSET 20` | `OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY`（12c+） | `OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY` |
| **自增主键** | `AUTO_INCREMENT` | `SERIAL` / `GENERATED ALWAYS AS IDENTITY` | `SEQUENCE + TRIGGER` | `IDENTITY(1,1)` |
| **字符串拼接** | `CONCAT(a, b)` | `a || b` | `a || b` | `a + b` |
| **日期函数** | `NOW()` | `CURRENT_TIMESTAMP` | `SYSDATE` | `GETDATE()` |
| **大小写** | 默认不敏感 | 敏感（需加引号） | 默认大写 | 可配置 |
| **布尔类型** | `TINYINT(1)` | `BOOLEAN` | `NUMBER(1)` | `BIT` |
| **JSON 支持** | `JSON` 类型（5.7+） | `JSONB`（原生强大） | `CLOB` 存储 | `NVARCHAR(MAX)` |
| **全文搜索** | `FULLTEXT` 索引 | `tsvector` + `GIN` | `Oracle Text` | `CONTAINS` |
| **连接字符串** | `jdbc:mysql://` | `jdbc:postgresql://` | `jdbc:oracle:thin:@` | `jdbc:sqlserver://` |

### 9.3 SQL 方言抽象层实现

```python
from abc import ABC, abstractmethod
from enum import Enum

class DatabaseType(Enum):
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    ORACLE = "oracle"
    SQL_SERVER = "sqlserver"

class DatabaseAdapter(ABC):
    """数据库方言抽象接口，各数据库实现各自的适配。"""

    @abstractmethod
    def paginate(self, sql: str, offset: int, limit: int) -> str:
        """分页 SQL 适配"""
        pass

    @abstractmethod
    def date_now(self) -> str:
        """当前时间函数"""
        pass

    @abstractmethod
    def string_concat(self, *fields: str) -> str:
        """字符串拼接"""
        pass

    @abstractmethod
    def get_driver(self) -> str:
        """Python 驱动"""
        pass


class MySQLAdapter(DatabaseAdapter):
    def paginate(self, sql, offset, limit):
        return f"{sql} LIMIT {limit} OFFSET {offset}"

    def date_now(self):
        return "NOW()"

    def string_concat(self, *fields):
        return f"CONCAT({', '.join(fields)})"

    def get_driver(self):
        return "aiomysql"


class PostgreSQLAdapter(DatabaseAdapter):
    def paginate(self, sql, offset, limit):
        return f"{sql} LIMIT {limit} OFFSET {offset}"

    def date_now(self):
        return "CURRENT_TIMESTAMP"

    def string_concat(self, *fields):
        return " || ".join(fields)

    def get_driver(self):
        return "asyncpg"


class OracleAdapter(DatabaseAdapter):
    def paginate(self, sql, offset, limit):
        return f"{sql} OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY"

    def date_now(self):
        return "SYSDATE"

    def string_concat(self, *fields):
        return " || ".join(fields)

    def get_driver(self):
        return "cx_Oracle_async"


class SQLServerAdapter(DatabaseAdapter):
    def paginate(self, sql, offset, limit):
        return f"{sql} OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY"

    def date_now(self):
        return "GETDATE()"

    def string_concat(self, *fields):
        return " + ".join(fields)

    def get_driver(self):
        return "aioodbc"


# 工厂方法：根据配置自动选择适配器
ADAPTER_REGISTRY = {
    DatabaseType.MYSQL: MySQLAdapter,
    DatabaseType.POSTGRESQL: PostgreSQLAdapter,
    DatabaseType.ORACLE: OracleAdapter,
    DatabaseType.SQL_SERVER: SQLServerAdapter,
}

def get_adapter(db_type: DatabaseType) -> DatabaseAdapter:
    adapter_cls = ADAPTER_REGISTRY.get(db_type)
    if not adapter_cls:
        raise ValueError(f"不支持的数据库类型: {db_type}")
    return adapter_cls()
```

### 9.4 分页查询适配

```python
class UniversalPaginator:
    """跨数据库统一分页查询。"""

    def __init__(self, adapter: DatabaseAdapter, session, base_query: str, params: dict):
        self.adapter = adapter
        self.session = session
        self.base_query = base_query
        self.params = params

    async def page(self, page_num: int = 1, page_size: int = 20) -> dict:
        offset = (page_num - 1) * page_size
        # 使用适配器生成分页 SQL
        paginated_sql = self.adapter.paginate(self.base_query, offset, page_size)

        result = await self.session.execute(paginated_sql, self.params)
        rows = result.fetchall()

        # 查询总数（用子查询包装）
        count_sql = f"SELECT COUNT(*) FROM ({self.base_query}) AS _total"
        total = await self.session.scalar(count_sql, self.params)

        return {
            "data": [dict(row) for row in rows],
            "pagination": {
                "page": page_num,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size,
            }
        }
```

---

## 十、完整代码实现

### 10.1 Python 端完整实现（SQLAlchemy + 异步）

```python
"""
Agent 数据库接入完整实现（Python 端）
技术栈：SQLAlchemy 2.0 async + asyncpg + FastAPI
"""
import os, time, logging
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy import select, text, event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from fastapi import FastAPI, HTTPException, Depends

# ============ 配置层 ============
DB_CONFIG = {
    "master_url": os.getenv("DB_MASTER_URL",
        "postgresql+asyncpg://agent_writer:password@10.0.1.10:5432/business_db"),
    "slave_url": os.getenv("DB_SLAVE_URL",
        "postgresql+asyncpg://agent_reader:password@10.0.1.20:5432/business_db"),
    "pool_size": 20,
    "max_overflow": 10,
    "pool_timeout": 30,
    "pool_recycle": 1800,
    "statement_timeout_ms": 30000,
}

# 白名单表配置
ALLOWED_TABLES = {
    "documents", "doc_chunks", "doc_categories",
    "products", "orders_summary", "customer_public"
}

LOG = logging.getLogger("AgentDB")

# ============ 引擎初始化 ============
def create_engine_with_config(url: str) -> create_async_engine:
    return create_async_engine(
        url,
        pool_size=DB_CONFIG["pool_size"],
        max_overflow=DB_CONFIG["max_overflow"],
        pool_timeout=DB_CONFIG["pool_timeout"],
        pool_recycle=DB_CONFIG["pool_recycle"],
        pool_pre_ping=True,  # 使用前检查连接
        connect_args={
            "server_settings": {
                "statement_timeout": str(DB_CONFIG["statement_timeout_ms"]),
                "lock_timeout": "5000",
            }
        }
    )

master_engine = create_engine_with_config(DB_CONFIG["master_url"])
slave_engine = create_engine_with_config(DB_CONFIG["slave_url"])

MasterSession = async_sessionmaker(master_engine, expire_on_commit=False)
SlaveSession = async_sessionmaker(slave_engine, expire_on_commit=False)

# ============ 数据模型 ============
class Base(DeclarativeBase):
    pass

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    content: Mapped[str]
    dept_id: Mapped[int]
    tenant_id: Mapped[int]
    created_at: Mapped[datetime]

# ============ 安全层：五重防护集成 ============
class SafeQueryExecutor:
    """集成五重 SQL 注入防护的安全查询执行器。"""

    def __init__(self, audit_logger, circuit_breaker):
        self.audit = audit_logger
        self.breaker = circuit_breaker

    async def execute_read(self, session: AsyncSession, sql: str,
                          params: dict, user: dict, trace_id: str) -> List[Dict]:
        """
        安全执行只读查询，完整流程：
        1. 输入校验 → 2. 语义检测 → 3. 参数化执行 → 4. 结果脱敏 → 5. 审计
        """
        start_time = time.time()

        try:
            # 第一重：输入校验
            for key, val in params.items():
                cleaned = InputValidator.validate(str(val))
                if cleaned is None:
                    await self.audit.log(user["id"], "agent", sql, params, [],
                                        "blocked", 0, 0, trace_id)
                    raise HTTPException(400, f"参数 {key} 包含非法字符")

            # 第二重：SQL 语义检测
            check = SQLSemanticChecker.check(sql, ALLOWED_TABLES, allow_write=False)
            if not check["safe"]:
                await self.audit.log(user["id"], "agent", sql, params, [],
                                    "blocked", 0, 0, trace_id)
                raise HTTPException(403, f"SQL 安全检测未通过: {check['reasons']}")

            # 第三重：参数化执行（text() 自动参数化）
            stmt = text(sql)
            result = await session.execute(stmt, params)
            rows = result.fetchall()

            # 第四重：结果脱敏
            desensitizer = ColumnLevelDesensitizer()
            safe_rows = [desensitizer.desensitize(dict(row), user["role"]) for row in rows]

            # 第五重：审计日志
            latency_ms = (time.time() - start_time) * 1000
            await self.audit.log(
                user["id"], "agent", sql, params, list(ALLOWED_TABLES),
                "success", len(safe_rows), latency_ms, trace_id
            )

            return safe_rows

        except HTTPException:
            raise
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            await self.audit.log(user["id"], "agent", sql, params, [],
                                "error", 0, latency_ms, trace_id)
            LOG.error(f"查询执行失败: {e}", exc_info=True)
            raise HTTPException(500, "查询执行失败")


# ============ 数据访问层 ============
class DocumentRepository:
    """文档数据访问层，所有方法都走安全执行器。"""

    def __init__(self, executor: SafeQueryExecutor):
        self.executor = executor

    async def search_by_keyword(self, keyword: str, user: dict,
                                trace_id: str, limit: int = 20) -> List[Dict]:
        sql = """SELECT id, title, LEFT(content, 200) as preview, dept_id, created_at
                 FROM documents
                 WHERE title LIKE :keyword
                   AND dept_id = ANY(:depts)
                   AND tenant_id = :tenant_id
                 ORDER BY created_at DESC
                 LIMIT :limit"""
        params = {
            "keyword": f"%{keyword}%",
            "depts": user["accessible_depts"],
            "tenant_id": user["tenant_id"],
            "limit": min(limit, 100)  # 强制上限
        }
        async with SlaveSession() as session:
            return await self.executor.execute_read(session, sql, params, user, trace_id)


# ============ FastAPI 集成 ============
app = FastAPI(title="Agent DB Service")

@app.get("/api/documents/search")
async def search_documents(keyword: str, current_user: dict = Depends(get_current_user)):
    trace_id = generate_trace_id()
    repo = DocumentRepository(SafeQueryExecutor(audit_logger, circuit_breaker))
    results = await repo.search_by_keyword(keyword, current_user, trace_id)
    return {"data": results, "trace_id": trace_id}
```

### 10.2 Java 端完整实现（MyBatis + HikariCP）

```java
/**
 * Agent 数据库接入完整实现（Java 端）
 * 技术栈：Spring Boot 3 + MyBatis-Plus + HikariCP + Spring Security
 */

// ============ 配置类 ============
@Configuration
public class DataSourceConfig {

    @Bean("masterDataSource")
    @ConfigurationProperties(prefix = "spring.datasource.master.hikari")
    public HikariDataSource masterDataSource() {
        HikariDataSource ds = new HikariDataSource();
        ds.setPoolName("AgentMasterPool");
        ds.setMaximumPoolSize(10);
        ds.setMinimumIdle(5);
        ds.setConnectionTimeout(30000);
        ds.setIdleTimeout(600000);
        ds.setMaxLifetime(1800000);
        ds.setLeakDetectionThreshold(60000);
        return ds;
    }

    @Bean("slaveDataSource")
    @ConfigurationProperties(prefix = "spring.datasource.slave.hikari")
    public HikariDataSource slaveDataSource() {
        HikariDataSource ds = new HikariDataSource();
        ds.setPoolName("AgentSlavePool");
        ds.setMaximumPoolSize(20);
        ds.setMinimumIdle(10);
        ds.setConnectionTimeout(30000);
        ds.setLeakDetectionThreshold(60000);
        return ds;
    }

    @Bean
    @Primary
    public DynamicDataSource dynamicDataSource(
            @Qualifier("masterDataSource") DataSource master,
            @Qualifier("slaveDataSource") DataSource slave) {
        DynamicDataSource dynamicDS = new DynamicDataSource();
        Map<Object, Object> targetDataSources = new HashMap<>();
        targetDataSources.put(DataSourceType.MASTER, master);
        targetDataSources.put(DataSourceType.SLAVE, slave);
        dynamicDS.setTargetDataSources(targetDataSources);
        dynamicDS.setDefaultTargetDataSource(slave); // 默认走从库
        return dynamicDS;
    }
}

// ============ 动态数据源路由 ============
public class DynamicDataSource extends AbstractRoutingDataSource {
    @Override
    protected Object determineCurrentLookupKey() {
        return DataSourceContextHolder.get();
    }
}

public class DataSourceContextHolder {
    private static final ThreadLocal<String> context = new ThreadLocal<>();

    public static void setMaster() { context.set("MASTER"); }
    public static void setSlave() { context.set("SLAVE"); }
    public static String get() { return context.get(); }
    public static void clear() { context.remove(); }
}

// ============ MyBatis Mapper ============
@Mapper
public interface DocumentMapper extends BaseMapper<Document> {

    // 参数化查询（#{} 自动防注入）
    @Select("SELECT id, title, LEFT(content, 200) as preview, dept_id, created_at " +
            "FROM documents WHERE title LIKE #{keyword} " +
            "AND dept_id IN <foreach collection='depts' item='d' open='(' separator=',' close=')'>#{d}</foreach> " +
            "AND tenant_id = #{tenantId} ORDER BY created_at DESC LIMIT #{limit}")
    List<DocumentDTO> searchByKeyword(@Param("keyword") String keyword,
                                       @Param("depts") List<Integer> depts,
                                       @Param("tenantId") Integer tenantId,
                                       @Param("limit") Integer limit);
}

// ============ 安全 Service ============
@Service
public class SafeDocumentService {

    @Autowired private DocumentMapper documentMapper;
    @Autowired private SqlSafetyChecker safetyChecker;
    @Autowired private SqlAuditLogger auditLogger;
    @Autowired private CircuitBreaker circuitBreaker;

    public List<DocumentDTO> searchDocuments(String keyword, UserContext user, String traceId) {
        long start = System.currentTimeMillis();

        try {
            // 1. 输入校验
            if (!InputValidator.validate(keyword)) {
                auditLogger.log(user.getId(), "agent", "search", keyword,
                               Collections.emptyList(), "blocked", 0, 0, traceId);
                throw new BusinessException(400, "输入包含非法字符");
            }

            // 2. 强制走从库
            DataSourceContextHolder.setSlave();

            // 3. 熔断检查
            if (!circuitBreaker.allowRequest()) {
                throw new ServiceException(503, "系统繁忙，请稍后重试");
            }

            // 4. 执行查询（MyBatis 自动参数化）
            int limit = Math.min(user.getDefaultLimit(), 100);
            List<DocumentDTO> results = documentMapper.searchByKeyword(
                "%" + keyword + "%", user.getAccessibleDepts(), user.getTenantId(), limit);

            // 5. 结果脱敏
            results = DataDesensitizer.desensitize(results, user.getRole());

            // 6. 审计
            long latency = System.currentTimeMillis() - start;
            auditLogger.log(user.getId(), "agent", "search", keyword,
                           results, "success", results.size(), latency, traceId);

            return results;

        } catch (Exception e) {
            long latency = System.currentTimeMillis() - start;
            auditLogger.log(user.getId(), "agent", "search", keyword,
                           Collections.emptyList(), "error", 0, latency, traceId);
            throw e;
        } finally {
            DataSourceContextHolder.clear();
        }
    }
}

// ============ Controller ============
@RestController
@RequestMapping("/api/documents")
public class DocumentController {

    @Autowired private SafeDocumentService documentService;

    @GetMapping("/search")
    public Result<List<DocumentDTO>> search(
            @RequestParam String keyword,
            @RequestHeader("X-User-Id") String userId,
            @RequestHeader("X-Trace-Id") String traceId) {
        UserContext user = authService.getUserContext(userId);
        List<DocumentDTO> data = documentService.searchDocuments(keyword, user, traceId);
        return Result.success(data, traceId);
    }
}
```

### 10.3 配置文件说明

```yaml
# agent_db_config.yaml 完整配置说明

# ============ 数据源配置 ============
datasources:
  master:                    # 主库（读写）
    url: jdbc:postgresql://10.0.1.10:5432/business_db
    username: agent_writer   # 从 Vault 读取，不硬编码
    password: ${Vault:db/master/password}
    driver: org.postgresql.Driver
    ssl: true                # 强制 SSL

  slave:                     # 只读副本
    url: jdbc:postgresql://10.0.1.20:5432/business_db
    username: agent_reader
    password: ${Vault:db/slave/password}
    driver: org.postgresql.Driver
    ssl: true

# ============ 连接池配置 ============
pool:
  master:
    max_size: 10             # 写操作少
    min_idle: 5
    timeout_ms: 30000
    idle_timeout_ms: 600000
    max_lifetime_ms: 1800000
    leak_detection_ms: 60000
  slave:
    max_size: 20             # 读操作多
    min_idle: 10
    timeout_ms: 30000
    idle_timeout_ms: 600000
    max_lifetime_ms: 1800000
    leak_detection_ms: 60000

# ============ 安全配置 ============
security:
  allowed_tables:            # 白名单表
    - documents
    - doc_chunks
    - products
    - orders_summary
  forbidden_tables:          # 黑名单表
    - mysql.user
    - information_schema.*
  pii_fields:                # PII 字段（自动脱敏）
    - phone
    - id_card
    - email
    - bank_card
  max_rows_per_query: 10000  # 单次查询上限
  query_timeout_sec: 30      # 查询超时

# ============ 限流配置 ============
rate_limit:
  qps: 50                    # 每秒最大查询数
  concurrent: 20             # 最大并发
  daily_quota: 100000        # 日查询配额

# ============ 熔断配置 ============
circuit_breaker:
  failure_threshold: 10      # 连续失败 10 次熔断
  recovery_timeout_sec: 60   # 60 秒后尝试恢复
  half_open_max_calls: 3     # 半开状态最多探测 3 次

# ============ 缓存配置 ============
cache:
  l1_memory_size: 1000       # 内存缓存条数
  l2_redis_ttl_sec: 300      # Redis 缓存 5 分钟
  cacheable_tables:          # 可缓存的表
    - products
    - doc_categories

# ============ 审计配置 ============
audit:
  enabled: true
  retention_days: 1095       # 审计日志保留 3 年
  real_time_alert: true      # 实时告警
  alert_threshold:
    blocked_count: 5         # 5 次拦截即告警
    large_affected_rows: 1000 # 影响 1000 行即告警
```

---

## 十一、测试验证步骤

### 11.1 功能测试（8 项）

| TC ID | 测试场景 | 步骤 | 预期结果 |
|:------|:--------|:-----|:--------|
| TC-F01 | 正常查询 | 输入合法关键词搜索文档 | 返回结果 ≤100 条，带脱敏 |
| TC-F02 | 分页查询 | 翻页查询第 2 页 | 返回正确的偏移数据 |
| TC-F03 | 多数据库适配 | 同一查询在 MySQL/PG 执行 | 结果一致，分页 SQL 正确 |
| TC-F04 | 读写分离 | SELECT 走从库，INSERT 走主库 | 路由正确 |
| TC-F05 | 行级权限 | A 部门用户查 B 部门数据 | 返回空结果 |
| TC-F06 | 列级脱敏 | 普通用户查询含手机号 | 手机号脱敏为 138****5678 |
| TC-F07 | 缓存命中 | 相同查询第二次执行 | 命中缓存，延迟 <5ms |
| TC-F08 | 审计日志 | 执行查询后查审计表 | 完整记录含 Trace ID |

### 11.2 安全测试（6 项）

| TC ID | 测试场景 | 攻击 Payload | 预期结果 |
|:------|:--------|:-----------|:--------|
| TC-S01 | SQL 注入 | `'; DROP TABLE documents; --` | 拦截 + 告警 |
| TC-S02 | UNION 注入 | `' UNION SELECT * FROM mysql.user --` | 拦截（白名单表） |
| TC-S03 | 时间盲注 | `'; SLEEP(10); --` | 拦截（黑名单关键词） |
| TC-S04 | 越权访问 | 普通用户访问 admin 表 | 403 拒绝 |
| TC-S05 | 大结果集 | 不带 LIMIT 的全表查询 | 强制注入 LIMIT 10000 |
| TC-S06 | 慢查询 | `SELECT * FROM huge_table` | 30s 超时 + 告警 |

### 11.3 性能测试（4 项）

| TC ID | 测试场景 | 指标 | 达标标准 |
|:------|:--------|:-----|:--------|
| TC-P01 | 并发查询 | 50 QPS 持续 10 分钟 | P95 延迟 <500ms |
| TC-P02 | 连接池压测 | 100 并发获取连接 | 无 PoolTimeout |
| TC-P03 | 缓存命中率 | 相同查询重复 100 次 | 命中率 ≥90% |
| TC-P04 | 熔断恢复 | 模拟 DB 故障后恢复 | 60s 内自动恢复 |

### 11.4 容灾测试（2 项）

| TC ID | 测试场景 | 步骤 | 预期结果 |
|:------|:--------|:-----|:--------|
| TC-D01 | 主库故障 | 主库宕机，Agent 查询 | 降级到从库，用户无感 |
| TC-D02 | 从库故障 | 从库宕机 | 熔断 + 降级返回友好提示 |

---

## 十二、与系列文档的集成关系

| 本文档章节 | 对接系列文档 | 集成关系 |
|:----------|:-----------|:--------|
| §3 身份认证 | [118 号 §7 安全策略](./118企业知识库Agent系统完整工程设计方案_架构数据流模型选型接口安全开发计划与测试.md) | 本文三层认证 → 118 §7.2 访问安全 |
| §4 数据访问 | [118 号 §4.2 知识存储模块](./118企业知识库Agent系统完整工程设计方案_架构数据流模型选型接口安全开发计划与测试.md) | 本文读写分离 → 118 三库协同 |
| §5 SQL 防注入 | [119 号 NFR-S06](./119企业知识库Agent项目系统性需求分析_目标用户功能非功能约束优先级验收与变更管控.md) | 本文五重防护 → 119 NFR-S06 注入拦截 99% |
| §6 连接池 | [118 号 §10 部署运维](./118企业知识库Agent系统完整工程设计方案_架构数据流模型选型接口安全开发计划与测试.md) | 本文连接池配置 → 118 §10.2 监控 |
| §8 性能优化 | [118 号 §9.2 性能测试](./118企业知识库Agent系统完整工程设计方案_架构数据流模型选型接口安全开发计划与测试.md) | 本文优化方案 → 118 性能基准 |
| §11 测试验证 | [119 号 §8 验收标准](./119企业知识库Agent项目系统性需求分析_目标用户功能非功能约束优先级验收与变更管控.md) | 本文 20 项测试 → 119 验收用例补充 |

> **文档结语**：
> 数据库是企业的核心数据资产，Agent 接入数据库**安全是底线、性能是保障、可观测是基础**。本文档的五层架构 + 五重防护 + 三层认证 + 多库适配方案，已在多家企业级 Agent 项目中验证可行。核心建议：**安全措施从 Day 1 就内置，而非事后补丁**——这是 Agent 数据库接入工程化的第一原则。
