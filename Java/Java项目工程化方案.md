# Java 项目工程化方案

> 本方案面向中大型 Java 项目，系统覆盖项目结构设计、构建流程规范、代码质量管控、版本控制策略、测试框架配置、CI/CD 流程、依赖管理机制、文档生成标准、开发环境统一配置等九大核心领域。方案遵循 Java 开发最佳实践，确保项目具备**可扩展性、可维护性、可测试性**，并提供具体实施步骤与工具选型建议，适合团队落地与持续演进。

---

## 目录

- [一、总体设计原则](#一总体设计原则)
- [二、项目结构设计](#二项目结构设计)
- [三、依赖管理机制](#三依赖管理机制)
- [四、构建流程规范](#四构建流程规范)
- [五、代码质量管控](#五代码质量管控)
- [六、版本控制策略](#六版本控制策略)
- [七、测试框架配置](#七测试框架配置)
- [八、持续集成与持续部署（CI/CD）](#八持续集成与持续部署cicd)
- [九、文档生成标准](#九文档生成标准)
- [十、开发环境统一配置](#十开发环境统一配置)
- [十一、实施路线图](#十一实施路线图)
- [附录 工具链速查表](#附录-工具链速查表)

---

## 一、总体设计原则

### 1.1 核心目标

| 目标 | 含义 | 衡量指标 |
| --- | --- | --- |
| **可扩展性** | 新功能可独立模块化加入，不影响既有代码 | 模块耦合度、新增功能改动范围 |
| **可维护性** | 代码易读、易改、易排查问题 | 圈复杂度、代码重复率、平均修复时长 |
| **可测试性** | 业务逻辑可被自动化测试覆盖 | 单测覆盖率、测试金字塔分层比例 |
| **可重复构建** | 任何环境任何时间构建结果一致 | 构建可重现性、环境一致性 |
| **可追溯性** | 每次变更可追溯到需求与提交 | Commit-Issue 关联、版本号规范 |

### 1.2 设计原则（SOLID + 工程实践）

```
┌──────────────────────────────────────────────────────────┐
│  单一职责 (SRP)  │  开闭原则 (OCP)  │  里氏替换 (LSP)     │
│  接口隔离 (ISP)  │  依赖倒置 (DIP)  │                     │
├──────────────────────────────────────────────────────────┤
│  约定优于配置  │  自动化优于手工  │  显式优于隐式         │
│  失败快速 (Fail Fast)  │  不可变优先  │  契约先行           │
└──────────────────────────────────────────────────────────┘
```

### 1.3 技术栈选型基线

| 层次 | 推荐选型 | 备选 |
| --- | --- | --- |
| JDK | OpenJDK 17（LTS） | JDK 21（LTS）、JDK 8（存量） |
| 构建工具 | Maven 3.9+ | Gradle 8+ |
| 框架 | Spring Boot 3.x | Spring Boot 2.7（JDK8） |
| ORM | MyBatis-Plus | JPA/Hibernate |
| 代码规范 | Alibaba Java Coding Guidelines | Google Java Style |
| 静态检查 | SonarQube + SpotBugs + ErrorProne | PMD、Checkstyle |
| 测试 | JUnit 5 + Mockito + AssertJ | TestNG、Spock |
| CI/CD | GitLab CI / GitHub Actions | Jenkins |
| 容器化 | Docker + Kubernetes | - |
| 文档 | Swagger/OpenAPI + Javadoc | Spring REST Docs |

---

## 二、项目结构设计

### 2.1 多模块 Maven 项目结构

采用**多模块 + 分层架构**，按职责拆分模块，按层次组织包。

```
my-project/
├── pom.xml                          # 父 POM，统一依赖与插件版本
├── README.md
├── .editorconfig                    # 编辑器配置统一
├── .gitignore
├── .gitattributes
├── docs/                            # 项目文档
│   ├── architecture/
│   ├── api/
│   └── decisions/                   # ADR（架构决策记录）
├── my-project-api/                  # 对外 API 契约（DTO、接口）
│   ├── src/main/java/
│   └── pom.xml
├── my-project-domain/               # 领域模型与核心业务逻辑
│   ├── src/main/java/
│   └── pom.xml
├── my-project-application/          # 应用服务（用例编排）
│   ├── src/main/java/
│   └── pom.xml
├── my-project-infrastructure/       # 基础设施（DB、MQ、外部接口）
│   ├── src/main/java/
│   ├── src/main/resources/
│   └── pom.xml
├── my-project-web/                  # Web 入口（Controller、网关适配）
│   ├── src/main/java/
│   ├── src/main/resources/
│   └── pom.xml
├── my-project-startup/              # 启动模块（main 类、配置聚合）
│   ├── src/main/java/
│   ├── src/main/resources/
│   │   ├── application.yml
│   │   ├── application-dev.yml
│   │   ├── application-test.yml
│   │   └── application-prod.yml
│   └── pom.xml
└── my-project-test/                 # 集成测试、E2E 测试
    ├── src/test/java/
    └── pom.xml
```

### 2.2 单模块内部分层包结构

以 `my-project-web` 为例：

```
com.company.project.web
├── controller/              # HTTP 入口，仅做参数校验与转发
│   ├── OrderController.java
│   └── advice/              # 全局异常处理
│       └── GlobalExceptionHandler.java
├── dto/                     # 请求/响应 DTO
│   ├── request/
│   └── response/
├── converter/               # DTO ↔ 领域对象转换
│   └── OrderConverter.java
├── config/                  # Web 相关配置
│   ├── WebMvcConfig.java
│   └── SwaggerConfig.java
└── filter/                  # 过滤器、拦截器
    └── TraceIdFilter.java
```

### 2.3 领域模块（DDD 分层）

```
com.company.project.domain
├── order/                   # 订单聚合
│   ├── model/               # 实体、值对象、聚合根
│   │   ├── Order.java            ← 聚合根
│   │   ├── OrderItem.java        ← 实体
│   │   └── OrderStatus.java      ← 值对象（枚举）
│   ├── event/               # 领域事件
│   │   └── OrderCreatedEvent.java
│   ├── service/             # 领域服务
│   │   └── OrderDomainService.java
│   └── repository/          # 仓储接口（实现放 infrastructure）
│       └── OrderRepository.java
├── user/                    # 用户聚合
└── shared/                  # 共享内核（通用值对象、基础类）
    ├── model/
    │   └── Money.java
    └── exception/
        └── BusinessException.java
```

### 2.4 命名规范

| 类型 | 规则 | 示例 |
| --- | --- | --- |
| 包名 | 全小写、单数、反向域名 | `com.company.project.order` |
| 类名 | 大驼峰 | `OrderService` |
| 方法名 | 小驼峰、动词开头 | `createOrder` |
| 常量 | 全大写下划线 | `MAX_RETRY_TIMES` |
| 接口 | 不加 `I` 前缀 | `OrderRepository`（非 `IOrderRepository`） |
| 实现类 | `Impl` 后缀 | `OrderRepositoryImpl` |
| 测试类 | 被测类名 + `Test` | `OrderServiceTest` |
| 测试方法 | `should_期望行为_当_条件` | `should_throw_exception_when_stock_not_enough` |

### 2.5 资源文件组织

```
src/main/resources/
├── application.yml              # 主配置
├── application-{profile}.yml    # 环境配置
├── bootstrap.yml                # 启动前配置（如配置中心）
├── logback-spring.xml           # 日志配置
├── mapper/                      # MyBatis XML
│   └── OrderMapper.xml
├── db/
│   ├── migration/               # Flyway 迁移脚本
│   │   ├── V1.0.0__init_schema.sql
│   │   └── V1.0.1__add_order_index.sql
│   └── seed/                    # 初始化数据
└── i18n/                        # 国际化
    ├── messages_zh_CN.properties
    └── messages_en_US.properties
```

### 2.6 设计要点

1. **依赖方向单向**：`web → application → domain ← infrastructure`，domain 不依赖任何外层
2. **api 模块独立**：对外契约单独打包，供消费方引用，避免暴露内部实现
3. **startup 聚合启动**：只有一个模块含 `main` 方法，便于打包与运维
4. **测试分层**：单测在各模块 `src/test`，集成测试统一在 `my-project-test`

---

## 三、依赖管理机制

### 3.1 依赖管理总体策略

```
父 POM（dependencyManagement 统一版本）
   ↓
各子模块仅声明 groupId:artifactId，不写 version
   ↓
BOM（Bill of Materials）导入第三方大版本集合
```

### 3.2 父 POM 依赖管理

```xml
<project>
    <groupId>com.company</groupId>
    <artifactId>my-project-parent</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <packaging>pom</packaging>

    <properties>
        <java.version>17</java.version>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>

        <!-- 框架版本统一管理 -->
        <spring-boot.version>3.2.0</spring-boot.version>
        <mybatis-plus.version>3.5.5</mybatis-plus.version>
        <lombok.version>1.18.30</lombok.version>
        <mapstruct.version>1.5.5.Final</mapstruct.version>
        <junit.version>5.10.1</junit.version>
        <mockito.version>5.7.0</mockito.version>
    </properties>

    <!-- 导入 Spring Boot BOM，统一管理 Spring 全家桶版本 -->
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-dependencies</artifactId>
                <version>${spring-boot.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>

            <!-- 自研模块版本 -->
            <dependency>
                <groupId>com.company</groupId>
                <artifactId>my-project-api</artifactId>
                <version>${project.version}</version>
            </dependency>

            <!-- 第三方依赖显式声明版本 -->
            <dependency>
                <groupId>com.baomidou</groupId>
                <artifactId>mybatis-plus-boot-starter</artifactId>
                <version>${mybatis-plus.version}</version>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <build>
        <pluginManagement>
            <!-- 插件版本统一管理，见第四节 -->
        </pluginManagement>
    </build>
</project>
```

### 3.3 子模块依赖声明

子模块**只声明 groupId + artifactId**，版本由父 POM 统一管理：

```xml
<!-- my-project-web/pom.xml -->
<project>
    <parent>
        <groupId>com.company</groupId>
        <artifactId>my-project-parent</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>
    <artifactId>my-project-web</artifactId>

    <dependencies>
        <!-- 自研模块 -->
        <dependency>
            <groupId>com.company</groupId>
            <artifactId>my-project-application</artifactId>
        </dependency>
        <dependency>
            <groupId>com.company</groupId>
            <artifactId>my-project-api</artifactId>
        </dependency>

        <!-- Spring Boot Web（版本由 BOM 管理） -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- 工具库 -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <scope>provided</scope>
        </dependency>
    </dependencies>
</project>
```

### 3.4 依赖范围（scope）规范

| scope | 用途 | 是否打入最终包 | 典型场景 |
| --- | --- | --- | --- |
| `compile`（默认） | 编译+运行 | ✅ | Spring、工具库 |
| `provided` | 编译需、运行由容器提供 | ❌ | Lombok、Servlet API |
| `runtime` | 运行需、编译不需 | ✅ | JDBC 驱动 |
| `test` | 仅测试 | ❌ | JUnit、Mockito |
| `system` | 本地 jar（不推荐） | ❌ | 私有 jar，需配 systemPath |

### 3.5 依赖冲突排查与解决

```bash
# 查看依赖树
mvn dependency:tree

# 查看冲突（被覆盖的依赖）
mvn dependency:tree -Dverbose -Dincludes=com.google.guava:guava

# 排查未使用声明（声明了但未使用）
mvn dependency:analyze
# Used undeclared dependencies: 使用了但没声明（危险，靠传递依赖）
# Unused declared dependencies: 声明了但没使用（可清理）
```

**冲突解决原则**：

1. **最短路径优先**：A→B→C(v1) vs A→C(v2)，选 v2
2. **声明顺序优先**：同路径长度，先声明的胜出
3. **显式排除**：用 `<exclusions>` 排除不想要的传递依赖

```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>library-a</artifactId>
    <exclusions>
        <!-- 排除低版本 guava，使用项目统一版本 -->
        <exclusion>
            <groupId>com.google.guava</groupId>
            <artifactId>guava</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

### 3.6 依赖治理规则

1. **版本统一**：所有第三方版本在父 POM 集中管理，子模块禁止写 version
2. **禁止 SNAPSHOT 上生产**：发布分支必须用 RELEASE 版本
3. **定期升级**：每季度执行 `mvn versions:display-dependency-updates` 检查升级
4. **安全扫描**：CI 中集成 OWASP Dependency-Check 或 Snyk，发现 CVE 立即告警
5. **License 合规**：检查依赖 License（如 GPL 不允许引入闭源项目）

```xml
<!-- CI 中扫描依赖漏洞 -->
<plugin>
    <groupId>org.owasp</groupId>
    <artifactId>dependency-check-maven</artifactId>
    <version>9.0.9</version>
    <configuration>
        <failBuildOnCVSS>7</failBuildOnCVSS>  <!-- CVSS≥7 构建失败 -->
    </configuration>
</plugin>
```

---

## 四、构建流程规范

### 4.1 Maven 构建生命周期

```
validate → compile → test → package → verify → install → deploy
   │         │         │        │         │        │        │
   │         │         │        │         │        │        └─ 发布到私服
   │         │         │        │         │        └─ 安装到本地仓库
   │         │         │        │         └─ 集成测试、质量检查
   │         │         │        └─ 打包成 jar/war
   │         │         └─ 运行单元测试
   │         └─ 编译主代码
   └─ 校验项目与配置
```

### 4.2 父 POM 插件配置

```xml
<build>
    <pluginManagement>
        <plugins>
            <!-- 编译插件 -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.12.1</version>
                <configuration>
                    <source>${java.version}</source>
                    <target>${java.version}</target>
                    <encoding>UTF-8</encoding>
                    <parameters>true</parameters>  <!-- 保留参数名供反射 -->
                    <annotationProcessorPaths>
                        <path>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                            <version>${lombok.version}</version>
                        </path>
                        <path>
                            <groupId>org.mapstruct</groupId>
                            <artifactId>mapstruct-processor</artifactId>
                            <version>${mapstruct.version}</version>
                        </path>
                    </annotationProcessorPaths>
                </configuration>
            </plugin>

            <!-- 单元测试 -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.2.5</version>
                <configuration>
                    <parallel>methods</parallel>
                    <threadCount>4</threadCount>
                    <argLine>@{argLine} -Xmx1024m</argLine>
                </configuration>
            </plugin>

            <!-- 集成测试 -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-failsafe-plugin</artifactId>
                <version>3.2.5</version>
                <executions>
                    <execution>
                        <goals>
                            <goal>integration-test</goal>
                            <goal>verify</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>

            <!-- 代码覆盖率 -->
            <plugin>
                <groupId>org.jacoco</groupId>
                <artifactId>jacoco-maven-plugin</artifactId>
                <version>0.8.11</version>
                <executions>
                    <execution>
                        <id>prepare-agent</id>
                        <goals><goal>prepare-agent</goal></goals>
                    </execution>
                    <execution>
                        <id>report</id>
                        <phase>test</phase>
                        <goals><goal>report</goal></goals>
                    </execution>
                    <execution>
                        <id>check</id>
                        <goals><goal>check</goal></goals>
                        <configuration>
                            <rules>
                                <rule>
                                    <element>BUNDLE</element>
                                    <limits>
                                        <limit>
                                            <counter>LINE</counter>
                                            <value>COVEREDRATIO</value>
                                            <minimum>0.70</minimum>  <!-- 行覆盖率≥70% -->
                                        </limit>
                                    </limits>
                                </rule>
                            </rules>
                        </configuration>
                    </execution>
                </executions>
            </plugin>

            <!-- 代码规范检查 -->
            <plugin>
                <groupId>com.alibaba.alex</groupId>
                <artifactId>commons-p3c-pmd</artifactId>
                <version>2.1.1</version>
            </plugin>

            <!-- 打包（Spring Boot） -->
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <version>${spring-boot.version}</version>
                <executions>
                    <execution>
                        <goals><goal>repackage</goal></goals>
                    </execution>
                </executions>
            </plugin>

            <!-- 源码打包 -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-source-plugin</artifactId>
                <version>3.3.0</version>
                <executions>
                    <execution>
                        <id>attach-sources</id>
                        <goals><goal>jar-no-fork</goal></goals>
                    </execution>
                </executions>
            </plugin>

            <!-- Docker 镜像构建 -->
            <plugin>
                <groupId>com.google.cloud.tools</groupId>
                <artifactId>jib-maven-plugin</artifactId>
                <version>3.4.2</version>
                <configuration>
                    <from>
                        <image>eclipse-temurin:17-jre-alpine</image>
                    </from>
                    <to>
                        <image>registry.company.com/my-project:${project.version}</image>
                    </to>
                    <container>
                        <jvmFlags>
                            <jvmFlag>-Xms512m</jvmFlag>
                            <jvmFlag>-Xmx2g</jvmFlag>
                            <jvmFlag>-XX:+UseG1GC</jvmFlag>
                            <jvmFlag>-XX:+HeapDumpOnOutOfMemoryError</jvmFlag>
                        </jvmFlags>
                        <ports>
                            <port>8080</port>
                        </ports>
                    </container>
                </configuration>
            </plugin>
        </plugins>
    </pluginManagement>
</build>
```

### 4.3 构建 Profile

```xml
<profiles>
    <!-- 开发环境：跳过部分检查加速构建 -->
    <profile>
        <id>dev</id>
        <activation>
            <activeByDefault>true</activeByDefault>
        </activation>
        <properties>
            <skipTests>false</skipTests>
            <skipITs>true</skipITs>
            <sonar.skip>true</sonar.skip>
        </properties>
    </profile>

    <!-- CI 环境：全量检查 -->
    <profile>
        <id>ci</id>
        <properties>
            <skipTests>false</skipTests>
            <skipITs>false</skipITs>
            <sonar.skip>false</sonar.skip>
        </properties>
    </profile>

    <!-- 生产发布：跳过测试，加速打包 -->
    <profile>
        <id>release</id>
        <properties>
            <skipTests>true</skipTests>
        </properties>
        <build>
            <plugins>
                <!-- 发布时强制生成源码与文档包 -->
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-javadoc-plugin</artifactId>
                    <executions>
                        <execution>
                            <id>attach-javadocs</id>
                            <goals><goal>jar</goal></goals>
                        </execution>
                    </executions>
                </plugin>
                <!-- GPG 签名（如发布到中央仓库） -->
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-gpg-plugin</artifactId>
                    <executions>
                        <execution>
                            <phase>verify</phase>
                            <goals><goal>sign</goal></goals>
                        </execution>
                    </executions>
                </plugin>
            </plugins>
        </build>
    </profile>
</profiles>
```

### 4.4 构建命令规范

```bash
# 本地开发：快速编译+单测
mvn clean install -DskipITs

# CI 构建：全量检查
mvn clean verify -P ci

# 代码质量扫描
mvn clean verify sonar:sonar -P ci -Dsonar.host.url=http://sonar.company.com

# 生产发布
mvn clean deploy -P release

# 构建 Docker 镜像
mvn compile jib:build -P release

# 跳过测试快速打包（仅本地调试用，禁止 CI 使用）
mvn clean package -DskipTests
```

### 4.5 构建产物管理

```
target/
├── classes/                          # 编译后主代码
├── test-classes/                     # 编译后测试代码
├── my-project-web-1.0.0.jar         # 普通包
├── my-project-web-1.0.0.jar.original # 重命名前的原包
├── site/jacoco/                      # 覆盖率报告
│   └── index.html
├── checkstyle-result.xml             # 规范检查结果
├── surefire-reports/                 # 测试报告
└── failsafe-reports/                 # 集成测试报告
```

### 4.6 构建缓存与加速

```xml
<!-- 并行构建多模块 -->
<!-- 命令：mvn -T 1C clean install  （每核一个线程） -->

<!-- 跳过未变更模块（Maven 3.1+） -->
<!-- 命令：mvn clean install -rf :my-project-web -->

<!-- 增量编译 -->
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <configuration>
        <useIncrementalCompilation>true</useIncrementalCompilation>
    </configuration>
</plugin>
```

---

## 五、代码质量管控

### 5.1 质量管控体系

```
┌─────────────────────────────────────────────────────────┐
│  代码质量 = 规范 + 静态检查 + 单元测试 + Code Review + 度量 │
└─────────────────────────────────────────────────────────┘
        │           │           │            │          │
     Checkstyle  SpotBugs     JUnit       GitLab     SonarQube
     Alibaba     PMD         JaCoCo       PR         (度量平台)
     规范        ErrorProne                         覆盖率/重复/复杂度
```

### 5.2 代码规范（Checkstyle + Alibaba P3C）

`checkstyle.xml` 关键规则：

```xml
<module name="Checker">
    <module name="TreeWalker">
        <!-- 命名规范 -->
        <module name="TypeName"/>
        <module name="ConstantName"/>
        <module name="MethodName"/>
        <module name="ParameterName"/>

        <!-- 长度限制 -->
        <module name="LineLength">
            <property name="max" value="120"/>
        </module>
        <module name="MethodLength">
            <property name="max" value="80"/>
        </module>
        <module name="ParameterNumber">
            <property name="max" value="5"/>
        </module>

        <!-- 禁止 import 通配符 -->
        <module name="AvoidStarImport"/>

        <!-- 必须有 Javadoc（公开 API） -->
        <module name="JavadocMethod">
            <property name="scope" value="public"/>
        </module>

        <!-- 圈复杂度 -->
        <module name="CyclomaticComplexity">
            <property name="max" value="10"/>
        </module>

        <!-- 空块检查 -->
        <module name="EmptyBlock"/>
    </module>
</module>
```

Maven 集成：

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-checkstyle-plugin</artifactId>
    <version>3.3.1</version>
    <configuration>
        <configLocation>checkstyle.xml</configLocation>
        <failOnViolation>true</failOnViolation>
        <includeTestSourceDirectory>true</includeTestSourceDirectory>
    </configuration>
    <executions>
        <execution>
            <phase>verify</phase>
            <goals><goal>check</goal></goals>
        </execution>
    </executions>
</plugin>
```

### 5.3 静态代码分析

| 工具 | 关注点 | 集成方式 |
| --- | --- | --- |
| **SpotBugs**（FindBugs 继任） | 潜在 Bug（空指针、资源泄漏） | Maven 插件 |
| **PMD** | 代码坏味道、重复代码 | Maven 插件 |
| **Error Prone** | 编译期错误检测 | 编译器插件 |
| **SonarQube** | 综合质量平台（覆盖率、复杂度、漏洞、坏味道） | CI 集成 |

SpotBugs 配置：

```xml
<plugin>
    <groupId>com.github.spotbugs</groupId>
    <artifactId>spotbugs-maven-plugin</artifactId>
    <version>4.8.3.0</version>
    <configuration>
        <effort>Max</effort>
        <threshold>Low</threshold>  <!-- Low 级以上问题都报 -->
        <failOnError>true</failOnError>
        <plugins>
            <plugin>
                <groupId>com.h3xstream.findsecbugs</groupId>
                <artifactId>findsecbugs-plugin</artifactId>
                <version>1.12.0</version>
            </plugin>
        </plugins>
    </configuration>
    <executions>
        <execution>
            <phase>verify</phase>
            <goals><goal>check</goal></goals>
        </execution>
    </executions>
</plugin>
```

### 5.4 SonarQube 质量门禁

```yaml
# sonar-project.properties
sonar.projectKey=com.company:my-project
sonar.projectName=My Project
sonar.sources=src/main/java
sonar.tests=src/test/java
sonar.java.coveragePlugin=jacoco
sonar.coverage.jacoco.xmlReportPaths=target/site/jacoco/jacoco.xml
sonar.exclusions=**/generated/**,**/dto/**
sonar.coverage.exclusions=**/dto/**,**/config/**,**/*Application.java
```

**质量门禁（Quality Gate）规则**：

| 指标 | 阈值 | 说明 |
| --- | --- | --- |
| 新代码覆盖率 | ≥ 80% | 新增代码必须有测试 |
| 重复代码率 | < 3% | 新代码重复率 |
| 圈复杂度 | ≤ 15 | 单方法复杂度 |
| 严重问题 | 0 | Blocker/Critical 必须为 0 |
| 安全评级 | A | 安全漏洞评分 |

### 5.5 代码格式化（统一风格）

`.editorconfig` 统一编辑器行为：

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
indent_style = space
indent_size = 4
insert_final_newline = true
trim_trailing_whitespace = true

[*.{yml,yaml,json,xml}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false  # Markdown 末尾空格有语义
```

IDE 模板：导入 IDEA 的 `code-style.xml` 与 `inspection-profile.xml`，提交到仓库 `.idea/` 目录共享。

### 5.6 Code Review 规范

**PR 规则**：

1. **必须至少 2 人 Review**：1 人 Review + 1 人 Approve
2. **PR 描述模板**：
   ```markdown
   ## 变更说明
   [本次变更做了什么，为什么]
   
   ## 关联需求
   [Jira/Issue 链接]
   
   ## 测试方式
   [如何验证本次变更]
   
   ## 检查清单
   - [ ] 单测通过
   - [ ] 静态检查无新增问题
   - [ ] 无硬编码配置/密钥
   - [ ] 已更新文档
   ```

3. **Review 关注点**：
   - 业务逻辑正确性
   - 异常处理与边界条件
   - 安全漏洞（SQL 注入、XSS、敏感信息）
   - 性能（N+1 查询、大对象、循环低效）
   - 可读性（命名、注释、复杂度）

### 5.7 质量度量看板

SonarQube 提供以下看板（团队每周 Review）：

- **技术债**：Bad 代码累积的修复成本（人天），目标 < 30 天
- **趋势图**：覆盖率、问题数、重复率随时间变化
- **新代码质量**：最近一次发布后新增代码的质量

---

## 六、版本控制策略

### 6.1 Git 分支模型

采用 **Git Flow 简化版 + GitHub Flow** 混合模型：

```
main（生产分支，受保护）
  │
  ├── hotfix/1.0.1（紧急修复，从 main 拉出，合并回 main + develop）
  │
  └── develop（集成分支）
        │
        ├── feature/ORDER-123-create-order（功能分支，从 develop 拉出）
        │
        ├── feature/ORDER-124-payment
        │
        └── release/1.1.0（发布分支，从 develop 拉出，仅修 Bug）

┌──────────────────────────────────────────────────────────┐
│  main:      永远可部署，每个 commit 打 tag                 │
│  develop:   下一个版本的集成分支                            │
│  feature/*: 功能开发分支，命名 {type}/{ISSUE}-{desc}      │
│  release/*: 发布准备分支，只修 Bug 不加功能                │
│  hotfix/*:  紧急修复分支，从 main 拉出                    │
└──────────────────────────────────────────────────────────┘
```

### 6.2 分支保护规则

| 分支 | 保护规则 |
| --- | --- |
| `main` | 禁止直接 push；必须 PR + 2 人 Review + CI 通过；禁止 force push |
| `develop` | 禁止直接 push；必须 PR + 1 人 Review + CI 通过 |
| `release/*` | 仅 Release Manager 可合并；只允许修 Bug |

### 6.3 Commit Message 规范（Conventional Commits）

```
<type>(<scope>): <subject>

<body>

<footer>
```

**type 枚举**：

| type | 含义 |
| --- | --- |
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档变更 |
| `style` | 代码格式（不影响功能） |
| `refactor` | 重构（非 feat/fix） |
| `perf` | 性能优化 |
| `test` | 测试相关 |
| `build` | 构建/依赖变更 |
| `ci` | CI 配置变更 |
| `chore` | 杂项（不修改 src 或 test） |

**示例**：

```
feat(order): 支持订单拆单发货

- 新增 OrderSplitService 处理拆单逻辑
- Order 支持多个子订单关联
- 拆单后触发 OrderSplitEvent

Closes #ORDER-123
```

工具校验：用 commitlint 在 pre-commit hook 与 CI 中校验格式。

### 6.4 版本号规范（语义化版本 SemVer）

```
MAJOR.MINOR.PATCH
   │     │     │
   │     │     └─ 向后兼容的 Bug 修复
   │     └────── 向后兼容的新功能
   └──────────── 不兼容的 API 变更
```

**示例**：

- `1.0.0` → `1.0.1`：修 Bug
- `1.0.0` → `1.1.0`：加新功能
- `1.0.0` → `2.0.0`：不兼容变更

**版本管理工具**：`mvn versions:set -DnewVersion=1.2.0`

### 6.5 Tag 与发布

```bash
# 发布打 Tag
git tag -a v1.2.0 -m "Release 1.2.0"
git push origin v1.2.0

# CHANGELOG 自动生成（用 conventional-changelog）
npx conventional-changelog -p angular -i CHANGELOG.md -s
```

### 6.6 .gitignore 规范

```gitignore
# 编译产物
target/
*.class
build/
out/

# IDE
.idea/
*.iml
*.ipr
*.iws
.vscode/
.settings/
.project
.classpath

# 日志
*.log
logs/

# 敏感配置
application-local.yml
application-prod-secret.yml
*.pem
*.key

# OS
.DS_Store
Thumbs.db

# 临时文件
*.tmp
*.bak
*.swp
```

### 6.7 大文件与二进制管理

- **禁止提交 jar/war**：用 Maven 依赖管理，不直接提交二进制
- **大文件用 LFS**：超过 1MB 的二进制（图片、视频）用 `git lfs`
- **数据库脚本入库**：Flyway/Liquibase 迁移脚本必须入库

```bash
# 启用 LFS
git lfs install
git lfs track "*.psd" "*.zip"
git add .gitattributes
```

---

## 七、测试框架配置

### 7.1 测试金字塔

```
            ┌─────────┐
            │   E2E   │  10%  ← 端到端测试（慢、易碎、覆盖关键流程）
           ┌┴─────────┴┐
          │ Integration │  20%  ← 集成测试（Spring Context + 真实 DB/Testcontainers）
         ┌┴────────────┴┐
        │   Component    │  30%  ← 组件测试（单模块功能验证）
       ┌┴────────────────┴┐
      │      Unit Test     │  40%  ← 单元测试（快、独立、覆盖业务逻辑）
     └────────────────────┘
```

**比例原则**：底层多（快、稳）、顶层少（慢、易碎）。

### 7.2 单元测试（JUnit 5 + Mockito + AssertJ）

依赖：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
    <exclusions>
        <!-- 排除 JUnit 4，用 JUnit 5 -->
        <exclusion>
            <groupId>org.junit.vintage</groupId>
            <artifactId>junit-vintage-engine</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

测试示例（BDD 风格）：

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private InventoryClient inventoryClient;

    @InjectMocks
    private OrderService orderService;

    @Nested
    @DisplayName("创建订单")
    class CreateOrder {

        @Test
        @DisplayName("库存充足时创建订单成功")
        void should_create_order_when_stock_enough() {
            // Given
            OrderRequest request = OrderRequest.builder()
                .userId(1L).productId(100L).quantity(2).build();
            given(inventoryClient.checkStock(100L, 2)).willReturn(true);
            given(orderRepository.save(any())).willAnswer(inv -> {
                Order o = inv.getArgument(0);
                o.setId(1L);
                return o;
            });

            // When
            Order order = orderService.createOrder(request);

            // Then
            assertThat(order.getId()).isEqualTo(1L);
            assertThat(order.getStatus()).isEqualTo(OrderStatus.CREATED);
            verify(orderRepository).save(any());
        }

        @Test
        @DisplayName("库存不足时抛出业务异常")
        void should_throw_when_stock_not_enough() {
            // Given
            OrderRequest request = OrderRequest.builder()
                .productId(100L).quantity(10).build();
            given(inventoryClient.checkStock(100L, 10)).willReturn(false);

            // When & Then
            assertThatThrownBy(() -> orderService.createOrder(request))
                .isInstanceOf(BusinessException.class)
                .hasMessageContaining("库存不足");
        }
    }
}
```

### 7.3 集成测试（Testcontainers）

用 Testcontainers 启动真实数据库、Redis 等容器做集成测试：

```xml
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>testcontainers</artifactId>
    <version>1.19.3</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>mysql</artifactId>
    <version>1.19.3</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>1.19.3</version>
    <scope>test</scope>
</dependency>
```

集成测试示例：

```java
@SpringBootTest
@Testcontainers
class OrderRepositoryIT {

    @Container
    static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8.0")
        .withDatabaseName("test")
        .withUsername("test")
        .withPassword("test");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", mysql::getJdbcUrl);
        registry.add("spring.datasource.username", mysql::getUsername);
        registry.add("spring.datasource.password", mysql::getPassword);
    }

    @Autowired
    private OrderRepository orderRepository;

    @Test
    void should_save_and_find_order() {
        Order order = Order.builder().userId(1L).amount(BigDecimal.TEN).build();
        Order saved = orderRepository.save(order);

        assertThat(saved.getId()).isNotNull();
        assertThat(orderRepository.findById(saved.getId()))
            .isPresent()
            .get()
            .extracting(Order::getAmount)
            .isEqualTo(BigDecimal.TEN);
    }
}
```

### 7.4 Web 层测试（MockMvc + WireMock）

Controller 测试不启动完整 Spring Context，用 `@WebMvcTest`：

```java
@WebMvcTest(OrderController.class)
class OrderControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private OrderService orderService;

    @Test
    void should_return_400_when_request_invalid() throws Exception {
        mockMvc.perform(post("/api/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"productId\":null}"))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.message").value("productId 不能为空"));
    }

    @Test
    void should_return_201_when_create_success() throws Exception {
        given(orderService.createOrder(any())).willReturn(1L);

        mockMvc.perform(post("/api/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"productId\":100,\"quantity\":2}"))
            .andExpect(status().isCreated())
            .andExpect(header().string("Location", "/api/orders/1"));
    }
}
```

外部依赖用 WireMock 模拟：

```java
@SpringBootTest
class PaymentClientTest {

    @RegisterExtension
    static WireMockExtension wireMock = WireMockExtension.newInstance()
        .options(wireMockConfig().dynamicPort())
        .build();

    @Test
    void should_call_payment_api() {
        wireMock.stubFor(post(urlEqualTo("/api/pay"))
            .willReturn(aResponse()
                .withStatus(200)
                .withBody("{\"paymentId\":\"PAY123\"}")
                .withHeader("Content-Type", "application/json")));

        PaymentClient client = new PaymentClient(wireMock.baseUrl());
        PaymentResult result = client.pay(new PaymentRequest());

        assertThat(result.getPaymentId()).isEqualTo("PAY123");
    }
}
```

### 7.5 测试命名与组织规范

- **命名**：`should_期望行为_当_条件`（BDD 风格）
- **结构**：Given / When / Then 三段式
- **组织**：用 `@Nested` 按业务场景分组
- **隔离**：每个测试独立，不依赖执行顺序
- **断言**：用 AssertJ 流式断言（比 JUnit 原生断言更可读）

### 7.6 覆盖率目标

| 模块类型 | 行覆盖率 | 分支覆盖率 |
| --- | --- | --- |
| domain（核心业务） | ≥ 90% | ≥ 85% |
| application | ≥ 80% | ≥ 75% |
| web | ≥ 60% | ≥ 50% |
| infrastructure | ≥ 70% | ≥ 60% |

**强制规则**：新增代码覆盖率 < 80% 阻断 PR 合并。

### 7.7 测试数据管理

```java
// 用 Builder 模式构造测试数据
Order order = OrderBuilder.aOrder()
    .withUserId(1L)
    .withAmount(BigDecimal.TEN)
    .build();

// 测试夹具（Fixture）放 fixtures/ 目录
public class OrderBuilder {
    private Long id = 1L;
    private Long userId = 1L;
    private BigDecimal amount = BigDecimal.TEN;
    // ... 默认值

    public static OrderBuilder aOrder() { return new OrderBuilder(); }
    public OrderBuilder withUserId(Long uid) { this.userId = uid; return this; }
    public Order build() { return new Order(id, userId, amount); }
}
```

---

## 八、持续集成与持续部署（CI/CD）

### 8.1 CI/CD 整体流程

```
开发提交 PR → CI 流水线 → Code Review → 合并 → CD 流水线 → 部署
     │            │                         │             │
     │            │                         │             └─ 自动部署到测试/预发/生产
     │            │                         └─ 触发构建与部署
     │            └─ 编译+测试+质量检查
     └─ 触发 CI
```

### 8.2 GitLab CI 配置

`.gitlab-ci.yml`：

```yaml
# 定义阶段
stages:
  - build
  - test
  - quality
  - package
  - deploy

# 全局变量
variables:
  MAVEN_OPTS: "-Dmaven.repo.local=.m2/repository"
  DOCKER_REGISTRY: registry.company.com

# 缓存加速构建
cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - .m2/repository

# ========== 构建阶段 ==========
build:
  stage: build
  image: maven:3.9-eclipse-temurin-17
  script:
    - mvn compile -B --quiet
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH

# ========== 测试阶段 ==========
unit-test:
  stage: test
  image: maven:3.9-eclipse-temurin-17
  script:
    - mvn test -B
  artifacts:
    reports:
      junit:
        - "**/target/surefire-reports/TEST-*.xml"
    paths:
      - "**/target/site/jacoco/"
    expire_in: 1 week

integration-test:
  stage: test
  image: maven:3.9-eclipse-temurin-17
  services:
    - docker:24-dind
  script:
    - mvn verify -B -P ci -DskipUTs
  artifacts:
    reports:
      junit:
        - "**/target/failsafe-reports/TEST-*.xml"

# ========== 质量阶段 ==========
sonarqube:
  stage: quality
  image: maven:3.9-eclipse-temurin-17
  script:
    - mvn sonar:sonar -B
      -Dsonar.host.url=$SONAR_HOST
      -Dsonar.login=$SONAR_TOKEN
      -Dsonar.qualitygate.wait=true  # 等待质量门禁结果，失败则 CI 失败
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == "develop"

dependency-check:
  stage: quality
  image: maven:3.9-eclipse-temurin-17
  script:
    - mvn dependency-check:check -B
  allow_failure: false  # 有高危漏洞则失败

# ========== 打包阶段 ==========
package:
  stage: package
  image: maven:3.9-eclipse-temurin-17
  script:
    - mvn package -B -DskipTests -P release
    - mvn jib:build -P release
  rules:
    - if: $CI_COMMIT_BRANCH == "develop"
    - if: $CI_COMMIT_BRANCH =~ /^release\//
    - if: $CI_COMMIT_TAG

# ========== 部署阶段 ==========
deploy-test:
  stage: deploy
  image: bitnami/kubectl:1.28
  environment:
    name: test
  script:
    - kubectl set image deployment/my-project my-project=$DOCKER_REGISTRY/my-project:$CI_COMMIT_SHORT_SHA -n test
    - kubectl rollout status deployment/my-project -n test
  rules:
    - if: $CI_COMMIT_BRANCH == "develop"

deploy-prod:
  stage: deploy
  image: bitnami/kubectl:1.28
  environment:
    name: prod
  script:
    - kubectl set image deployment/my-project my-project=$DOCKER_REGISTRY/my-project:$CI_COMMIT_TAG -n prod
    - kubectl rollout status deployment/my-project -n prod
  rules:
    - if: $CI_COMMIT_TAG
  when: manual  # 生产需手动触发
```

### 8.3 GitHub Actions 配置

`.github/workflows/ci.yml`：

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup JDK
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: maven

      - name: Build
        run: mvn compile -B

      - name: Test
        run: mvn test -B

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./target/site/jacoco/jacoco.xml

      - name: SonarQube
        run: mvn sonar:sonar -B
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}

  package:
    needs: build-test
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: maven
      - name: Build Image
        run: mvn compile jib:build -P release
        env:
          DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
          DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
```

### 8.4 部署策略

| 策略 | 原理 | 适用场景 |
| --- | --- | --- |
| **滚动部署** | 逐步替换旧 Pod | 常规发布 |
| **蓝绿部署** | 新旧两套环境，切换流量 | 重大版本 |
| **金丝雀部署** | 先小流量验证，再全量 | 高风险变更 |
| **A/B 测试** | 按用户特征分流 | 功能实验 |

Kubernetes 金丝雀部署示例：

```yaml
# 用 Istio VirtualService 做流量切分
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
spec:
  http:
  - route:
    - destination:
        host: my-project
        subset: stable
      weight: 90
    - destination:
        host: my-project
        subset: canary
      weight: 10  # 10% 流量到金丝雀
```

### 8.5 回滚机制

```bash
# Kubernetes 回滚
kubectl rollout undo deployment/my-project -n prod
kubectl rollout undo deployment/my-project --to-revision=3 -n prod

# 数据库回滚：Flyway 不支持自动回滚，需手写 Undo 脚本
# V1.0.1__add_column.sql  →  U1.0.1__drop_column.sql
```

### 8.6 制品管理

- **Docker 镜像**：Harbor 私服，按 `项目名:版本号-短SHA` 打 Tag
- **Maven 制品**：Nexus 私服，区分 snapshot 与 release 仓库
- **版本追溯**：每个镜像打 Label 标记 Git Commit、构建时间、构建号

```dockerfile
# 镜像元数据
LABEL org.opencontainers.image.source="https://github.com/company/my-project"
LABEL org.opencontainers.image.revision="${GIT_COMMIT}"
LABEL org.opencontainers.image.created="${BUILD_TIME}"
LABEL org.opencontainers.image.version="${VERSION}"
```

---

## 九、文档生成标准

### 9.1 文档体系

```
┌─────────────────────────────────────────────────────┐
│  架构文档    │  API 文档   │  运维手册  │  变更日志   │
│  (ADR/C4)   │ (OpenAPI)  │ (Runbook) │ (CHANGELOG)│
├─────────────────────────────────────────────────────┤
│  开发指南    │  代码注释   │  README   │  决策记录   │
│ (Onboarding)│ (Javadoc)  │           │   (ADR)    │
└─────────────────────────────────────────────────────┘
```

### 9.2 README 规范

每个仓库根目录必须有 `README.md`，包含：

```markdown
# 项目名称

一句话项目简介。

## 功能特性
- 特性 1
- 特性 2

## 技术栈
- Java 17 / Spring Boot 3 / MySQL 8

## 快速开始
### 环境要求
- JDK 17+
- Maven 3.9+
- MySQL 8+

### 本地运行
\`\`\`bash
git clone <repo>
cd my-project
mvn spring-boot:run -pl my-project-startup
\`\`\`

## 项目结构
[链接到架构文档]

## 开发指南
- [开发规范](docs/dev-guide.md)
- [提交流程](docs/contributing.md)

## 部署
- [部署手册](docs/deploy.md)

## 贡献指南
请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)

## License
[License 类型]
```

### 9.3 API 文档（OpenAPI 3 + Swagger）

引入 `springdoc-openapi`：

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.3.0</version>
</dependency>
```

注解化 API 文档：

```java
@Tag(name = "订单", description = "订单相关接口")
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    @Operation(summary = "创建订单", description = "根据商品与数量创建订单")
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "创建成功"),
        @ApiResponse(responseCode = "400", description = "参数错误"),
        @ApiResponse(responseCode = "409", description = "库存不足")
    })
    @PostMapping
    public ResponseEntity<Long> createOrder(
        @Parameter(description = "订单请求", required = true)
        @Valid @RequestBody OrderRequest request
    ) {
        Long id = orderService.createOrder(request);
        return ResponseEntity.created(URI.create("/api/orders/" + id)).body(id);
    }
}
```

访问 `/swagger-ui.html` 查看交互式文档，访问 `/v3/api-docs` 获取 JSON。

### 9.4 Javadoc 规范

公开 API 必须有 Javadoc：

```java
/**
 * 创建订单。
 *
 * <p>根据商品 ID 与数量创建订单，会扣减库存。
 *
 * @param request 订单请求，不能为 null
 * @return 创建的订单 ID
 * @throws BusinessException 当库存不足时抛出
 * @throws IllegalArgumentException 当 request 为 null 时抛出
 * @see OrderRequest
 * @since 1.0.0
 * @author Zhang San
 */
public Long createOrder(OrderRequest request) { ... }
```

Maven 生成 Javadoc：

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-javadoc-plugin</artifactId>
    <version>3.6.3</version>
    <configuration>
        <doclint>none</doclint>  <!-- 关闭严格检查（可选） -->
        <failOnError>false</failOnError>
    </configuration>
    <executions>
        <execution>
            <id>attach-javadocs</id>
            <goals><goal>jar</goal></goals>
        </execution>
    </executions>
</plugin>
```

### 9.5 架构决策记录（ADR）

每个重要架构决策记录一个 Markdown 文件，放 `docs/decisions/`：

```markdown
# ADR-001: 选择 MyBatis-Plus 作为 ORM 框架

- 状态：已采纳
- 日期：2026-08-01
- 决策者：架构组

## 背景
项目需要 ORM 框架，候选有 JPA/Hibernate、MyBatis、MyBatis-Plus。

## 决策
选择 MyBatis-Plus。

## 理由
1. 团队熟悉度高
2. SQL 可控，便于优化
3. 内置分页、代码生成

## 后果
- 正面：开发效率高、SQL 灵活
- 负面：需要手写复杂 SQL，DTO 转换较多
- 缓解：用 MapStruct 减少样板代码

## 相关
- 替代方案：JPA（适合简单 CRUD，复杂查询不灵活）
```

### 9.6 变更日志（CHANGELOG）

格式遵循 [Keep a Changelog](https://keepachangelog.com/)：

```markdown
# Changelog

## [1.2.0] - 2026-08-01

### Added
- 订单拆单功能
- 支持微信支付

### Changed
- 升级 Spring Boot 到 3.2.0

### Fixed
- 修复高并发下库存超扣问题

### Removed
- 移除废弃的 /api/v1/orders 接口
```

自动生成：用 `conventional-changelog` 从 Commit Message 生成。

### 9.7 文档与代码同步

- **API 文档**：注解化，与代码同生命周期，禁止单独维护 Word/Confluence
- **架构图**：用 PlantUML 或 Mermaid 文本化，提交仓库，避免用 Visio 等二进制工具
- **CI 校验**：构建时检查 Javadoc 是否生成成功，README 链接是否有效

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

System(systemA, "订单系统", "处理订单")
SystemDb(dbA, "MySQL", "存储订单数据")
Rel(systemA, dbA, "读写")
@enduml
```

---

## 十、开发环境统一配置

### 10.1 JDK 统一

```bash
# 推荐 SDKMAN 管理多版本 JDK
curl -s "https://get.sdkman.io" | bash
sdk install java 17.0.10-tem

# 项目根目录放 .sdkmanrc，进入目录自动切换版本
# .sdkmanrc 内容：
java=17.0.10-tem
maven=3.9.6
```

### 10.2 Maven 配置统一

`~/.m2/settings.xml` 团队统一模板：

```xml
<settings>
    <localRepository>${user.home}/.m2/repository</localRepository>

    <!-- 私服认证 -->
    <servers>
        <server>
            <id>company-nexus</id>
            <username>${env.NEXUS_USER}</username>
            <password>${env.NEXUS_PASS}</password>
        </server>
    </servers>

    <!-- 镜像与仓库 -->
    <mirrors>
        <mirror>
            <id>aliyun</id>
            <mirrorOf>central</mirrorOf>
            <url>https://maven.aliyun.com/repository/public</url>
        </mirror>
    </mirrors>

    <!-- Profile 激活 -->
    <profiles>
        <profile>
            <id>company</id>
            <repositories>
                <repository>
                    <id>company-nexus</id>
                    <url>https://nexus.company.com/repository/maven-public/</url>
                    <releases><enabled>true</enabled></releases>
                    <snapshots><enabled>true</enabled></snapshots>
                </repository>
            </repositories>
        </profile>
    </profiles>

    <activeProfiles>
        <activeProfile>company</activeProfile>
    </activeProfiles>
</settings>
```

### 10.3 IDE 配置统一（IntelliJ IDEA）

提交以下配置到仓库 `.idea/` 或 `.vscode/`：

- `code-style.xml`：代码格式化规则
- `inspection-profiles/Project_Default.xml`：检查规则
- `encodings.xml`：UTF-8 统一编码
- `copyright/Apache.xml`：版权头模板

**IDEA 推荐插件**（团队统一）：

| 插件 | 用途 |
| --- | --- |
| Lombok | 支持 Lombok 注解 |
| MapStruct Support | MapStruct 代码提示 |
| SonarLint | 实时质量检查 |
| Checkstyle-IDEA | 规范检查 |
| Maven Helper | 依赖冲突排查 |
| GitToolBox | Git 增强 |
| Rainbow Brackets | 括号彩色配对 |
| GenerateAllSetter | 一键生成 setter |

### 10.4 Git Hooks 统一

用 `pre-commit` 框架管理 hooks，配置提交仓库：

`.pre-commit-config.yaml`：

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-merge-conflict

  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v3.0.0
    hooks:
      - id: conventional-pre-commit  # 校验 commit message

  - repo: https://github.com/Ek0r0n/pre-commit-java
    rev: v0.4.0
    hooks:
      - id: checkstyle
        args: [-c, checkstyle.xml]
```

安装：

```bash
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg  # 安装 commit-msg hook
```

### 10.5 本地开发数据库（Docker Compose）

`docker-compose.yml` 一键启动依赖：

```yaml
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    ports: ["3306:3306"]
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: my_project
    volumes:
      - mysql-data:/var/lib/mysql
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  # 模拟外部服务
  wiremock:
    image: wiremock/wiremock:3.3.1
    ports: ["8081:8080"]
    volumes:
      - ./wiremock/mappings:/home/wiremock/mappings

volumes:
  mysql-data:
```

`make dev` 或 `docker-compose up -d` 一键拉起完整开发环境。

### 10.6 环境变量与配置

```
.env.example          # 提交到仓库，列出所需变量
.env                  # 本地实际值，加入 .gitignore
```

```bash
# .env.example
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
REDIS_HOST=localhost
NEXUS_USER=
NEXUS_PASS=
```

新人入职：`cp .env.example .env` → 填入本地值 → 即可开发。

### 10.7 Makefile 统一命令

```makefile
.PHONY: dev build test clean package docker

dev:
	docker-compose up -d
	mvn spring-boot:run -pl my-project-startup

build:
	mvn clean install -DskipITs

test:
	mvn test

clean:
	mvn clean

package:
	mvn clean package -DskipTests -P release

docker:
	mvn compile jib:dockerBuild -P release

lint:
	mvn checkstyle:check spotbugs:check

sonar:
	mvn sonar:sonar
```

新人只需记住 `make dev` 即可启动开发。

---

## 十一、实施路线图

### 11.1 分阶段落地

```
┌─────────────────────────────────────────────────────────────┐
│ 阶段一（1-2 周）：基础设施搭建                                │
│ - 多模块骨架搭建、父 POM 统一依赖                            │
│ - Git 仓库初始化、分支模型、.gitignore                       │
│ - IDE 配置统一、EditorConfig                                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 阶段二（2-3 周）：质量体系搭建                                │
│ - Checkstyle + SpotBugs + Alibaba 规范接入                  │
│ - JUnit 5 + Mockito + AssertJ 测试框架                      │
│ - JaCoCo 覆盖率统计                                          │
│ - SonarQube 接入                                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 阶段三（2-3 周）：CI/CD 流水线                                │
│ - GitLab CI / GitHub Actions 配置                            │
│ - 自动构建、测试、质量门禁                                    │
│ - Docker 镜像构建与推送                                      │
│ - K8s 自动部署（测试/预发）                                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 阶段四（持续）：优化与演进                                    │
│ - 监控告警（Prometheus + Grafana）                          │
│ - 链路追踪（SkyWalking / Jaeger）                            │
│ - 日志聚合（ELK）                                            │
│ - 自动化测试增强（契约测试、性能测试）                        │
└─────────────────────────────────────────────────────────────┘
```

### 11.2 团队规范落地

1. **培训**：每引入一项规范，组织 1 小时分享会
2. **Code Review 卡点**：PR 必须过 CI + 人工 Review
3. **度量**：每月统计覆盖率、缺陷率、构建时长，持续改进
4. **复盘**：每次线上事故复盘，补充测试用例与规范

### 11.3 度量指标

| 指标 | 目标 | 衡量方式 |
| --- | --- | --- |
| 单测覆盖率 | ≥ 80% | JaCoCo |
| 构建时长 | < 10 分钟 | CI 记录 |
| CI 成功率 | ≥ 95% | GitLab/GitHub 统计 |
| PR 评审时长 | < 4 小时 | 平台统计 |
| 缺陷逃逸率 | < 5% | 生产 Bug / 总 Bug |
| 部署频率 | 每周 ≥ 2 次 | 部署记录 |
| 平均修复时长（MTTR） | < 1 小时 | 事故记录 |

---

## 附录 工具链速查表

| 类别 | 工具 | 用途 | 备注 |
| --- | --- | --- | --- |
| **构建** | Maven 3.9+ | 依赖管理与构建 | 推荐 |
| | Gradle 8+ | 替代 Maven | 灵活、速度快 |
| **代码规范** | Checkstyle | 风格检查 | |
| | Alibaba P3C | 阿里规范 | 中文社区友好 |
| | SpotBugs | Bug 检测 | FindBugs 继任 |
| | Error Prone | 编译期检查 | Google 出品 |
| **测试** | JUnit 5 | 单测框架 | |
| | Mockito | Mock 框架 | |
| | AssertJ | 流式断言 | |
| | Testcontainers | 集成测试容器 | |
| | WireMock | HTTP Mock | |
| | JaCoCo | 覆盖率 | |
| **质量平台** | SonarQube | 综合质量 | |
| | OWASP Dependency-Check | 漏洞扫描 | |
| **CI/CD** | GitLab CI | CI/CD 平台 | |
| | GitHub Actions | CI/CD 平台 | |
| | Jenkins | CI/CD 平台 | 老牌 |
| | Harbor | 镜像私服 | |
| | Nexus | Maven 私服 | |
| **容器** | Docker | 容器化 | |
| | Kubernetes | 编排 | |
| | Jib | Java 镜像构建 | 免 Dockerfile |
| **文档** | springdoc-openapi | API 文档 | Swagger UI |
| | PlantUML / Mermaid | 架构图 | 文本化 |
| | Javadoc | 代码文档 | |
| **版本控制** | Git | 版本控制 | |
| | pre-commit | Hook 管理 | |
| | conventional-changelog | CHANGELOG 生成 | |
| **开发环境** | SDKMAN | JDK 管理 | |
| | Docker Compose | 本地依赖 | |
| | Make | 命令统一 | |
| **监控** | Prometheus + Grafana | 指标监控 | |
| | ELK / Loki | 日志聚合 | |
| | SkyWalking / Jaeger | 链路追踪 | |

---

## 参考资料

- [Maven 官方文档](https://maven.apache.org/guides/)
- [Spring Boot Reference](https://docs.spring.io/spring-boot/docs/current/reference/html/)
- [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html)
- [Alibaba Java Coding Guidelines](https://github.com/alibaba/p3c)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)
- [Testcontainers 官方文档](https://www.testcontainers.org/)
- [SonarQube 文档](https://docs.sonarsource.com/sonarqube/)
- [12-Factor App](https://12factor.net/zh_cn/)

---

> **文档说明**：本方案系统覆盖 Java 项目工程化的九大核心领域，提供具体工具选型、配置示例与实施步骤。建议团队按"实施路线图"分阶段落地，先建骨架再填血肉，避免一次性引入过多规范导致团队抵触。工程化的核心不是工具堆砌，而是通过约定与自动化，让团队把精力集中在业务价值交付上。
