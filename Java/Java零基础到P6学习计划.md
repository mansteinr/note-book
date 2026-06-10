# Java 零基础到 P6 级工程师系统学习计划

> **目标定位**：大厂 P6 级工程师（高级开发工程师），具备独立负责核心模块设计开发、技术方案评审、指导初级工程师的能力。
>
> **预计总时长**：6-8 个月（全日制学习）/ 10-12 个月（在职学习）

---

## 目录

- [第一阶段：Java 基础知识（6-8 周）](#第一阶段java-基础知识6-8-周)
- [第二阶段：Java 进阶技术（8-10 周）](#第二阶段java-进阶技术8-10-周)
- [第三阶段：Maven 项目管理（2-3 周）](#第三阶段maven-项目管理2-3-周)
- [第四阶段：Spring Boot 框架应用（8-10 周）](#第四阶段spring-boot-框架应用8-10-周)
- [第五阶段：综合实战项目（6-8 周）](#第五阶段综合实战项目6-8-周)
- [学习方法建议](#学习方法建议)
- [常见问题与解决方案](#常见问题与解决方案)
- [P6 面试能力清单](#p6-面试能力清单)

---

## 第一阶段：Java 基础知识（6-8 周）

### 学习目标
- 掌握 Java 核心语法与面向对象编程思想
- 熟练使用常用集合类与异常处理机制
- 理解 JVM 基本内存模型与类加载机制
- 能够独立完成 2000+ 行的小型控制台项目

### 详细内容与资源

#### 1.1 环境搭建与基础语法（第 1 周）

| 学习内容 | 重点 | 资源链接 |
|---|---|---|
| JDK 安装与配置 | JDK 17/21 LTS 版本选择、环境变量配置 | [Oracle JDK 下载](https://www.oracle.com/java/technologies/downloads/) |
| IDE 使用 | IntelliJ IDEA 安装、快捷键、调试技巧 | [IDEA 官方文档](https://www.jetbrains.com/idea/documentation/) |
| 基础语法 | 变量、数据类型、运算符、流程控制 | [Java Tutorials - Oracle](https://docs.oracle.com/javase/tutorial/java/nutsandbolts/index.html) |
| 数组 | 一维/二维数组、遍历、排序 | [Java Array 教程](https://docs.oracle.com/javase/tutorial/java/nutsandbolts/arrays.html) |

**练习**：编写一个学生成绩管理系统（控制台），支持成绩录入、查询、排序、统计功能。

---

#### 1.2 面向对象编程（第 2-3 周）

| 学习内容 | 重点 | 资源链接 |
|---|---|---|
| 类与对象 | 构造方法、this 关键字、static 关键字 | [Java OOP Concepts](https://docs.oracle.com/javase/tutorial/java/concepts/) |
| 封装 | 访问修饰符（private/default/protected/public） | [Controlling Access](https://docs.oracle.com/javase/tutorial/java/javaOO/accesscontrol.html) |
| 继承 | extends、super、方法重写、final | [Inheritance](https://docs.oracle.com/javase/tutorial/java/IandI/subclasses.html) |
| 多态 | 向上转型、向下转型、动态绑定 | [Polymorphism](https://docs.oracle.com/javase/tutorial/java/IandI/polymorphism.html) |
| 抽象类与接口 | abstract、interface、default 方法 | [Abstract Methods and Classes](https://docs.oracle.com/javase/tutorial/java/IandI/abstract.html) |
| 内部类 | 成员内部类、静态内部类、匿名内部类 | [Nested Classes](https://docs.oracle.com/javase/tutorial/java/javaOO/nested.html) |
| 枚举与注解 | enum、@Override、自定义注解 | [Enum Types](https://docs.oracle.com/javase/tutorial/java/javaOO/enum.html) |

**推荐课程**：
- [【慕课网】Java 入门第一季](https://www.imooc.com/learn/85)
- [【B 站】韩顺平 - 零基础 30 天学会 Java](https://www.bilibili.com/video/BV1fh411y7R8)

**练习**：设计一个简易的"图书管理系统"，包含借书、还书、查询等功能，要求使用继承和多态。

---

#### 1.3 常用类与 API（第 4 周）

| 学习内容 | 重点 | 资源链接 |
|---|---|---|
| String/StringBuilder/StringBuffer | 字符串不可变性、性能对比、常用方法 | [Java String 官方文档](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/String.html) |
| 包装类 | 自动装箱/拆箱、缓存机制、类型转换 | [Autoboxing and Unboxing](https://docs.oracle.com/javase/tutorial/java/data/autoboxing.html) |
| Object 类 | equals/hashCode/toString、深拷贝与浅拷贝 | [Object 类文档](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/Object.html) |
| 日期时间 API | LocalDate/LocalDateTime、DateTimeFormatter | [Java Date Time API](https://docs.oracle.com/javase/tutorial/datetime/) |
| Math/Random | 数学运算、随机数生成 | - |
| BigDecimal | 精确计算（金钱场景必备） | [BigDecimal 最佳实践](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/math/BigDecimal.html) |

---

#### 1.5 集合框架（第 5 周）

| 学习内容 | 重点 | 资源链接 |
|---|---|---|
| ArrayList / LinkedList | 底层数据结构、性能差异、扩容机制 | [List Implementations](https://docs.oracle.com/javase/tutorial/collections/implementations/list.html) |
| HashSet / TreeSet | 去重原理、红黑树、Comparable 接口 | [Set Implementations](https://docs.oracle.com/javase/tutorial/collections/implementations/set.html) |
| HashMap / TreeMap | 哈希冲突、红黑树转换、扩容 | [HashMap 源码分析 - CSDN](https://blog.csdn.net/weixin_43314519/article/details/121305499) |
| Iterator | fail-fast 机制、增强 for 循环原理 | [Collections Framework](https://docs.oracle.com/javase/tutorial/collections/) |
| Collections 工具类 | 排序、查找、同步包装 | [Collections 文档](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Collections.html) |
| Stream 基础 | map/filter/collect、函数式编程入门 | [Stream API](https://docs.oracle.com/javase/tutorial/collections/streams/) |

**面试重点**：HashMap 的 put/get 流程、扩容机制、为什么线程不安全。

---

#### 1.6 异常处理与 IO 流（第 6 周）

| 学习内容 | 重点 | 资源链接 |
|---|---|---|
| 异常体系 | Throwable/Error/Exception、检查型与非检查型异常 | [Exceptions](https://docs.oracle.com/javase/tutorial/essential/exceptions/) |
| try-catch-finally | 执行顺序、资源自动关闭（try-with-resources） | [The try-with-resources Statement](https://docs.oracle.com/javase/tutorial/essential/exceptions/tryResourceClose.html) |
| 自定义异常 | 业务异常设计、全局异常处理规范 | - |
| File / 字节流 / 字符流 | InputStream/OutputStream、Reader/Writer | [IO Streams](https://docs.oracle.com/javase/tutorial/essential/io/) |
| NIO 基础 | Buffer、Channel、Selector 概念 | [Java NIO 教程 - 廖雪峰](https://www.liaoxuefeng.com/wiki/1252599548343744/1255945227754976) |

**练习**：实现一个文件批量重命名工具，支持按规则批量重命名并输出操作日志。

---

#### 1.7 多线程基础（第 7-8 周）

| 学习内容 | 重点 | 资源链接 |
|---|---|---|
| 线程创建 | Thread、Runnable、Callable/Future | [Thread Objects](https://docs.oracle.com/javase/tutorial/essential/concurrency/threads.html) |
| 线程生命周期 | NEW/RUNNABLE/BLOCKED/WAITING/TERMINATED | - |
| synchronized | 对象锁、类锁、锁升级（偏向锁→轻量级锁→重量级锁） | [Synchronization](https://docs.oracle.com/javase/tutorial/essential/concurrency/sync.html) |
| volatile | 可见性、禁止指令重排、与 synchronized 区别 | - |
| wait/notify | 生产者消费者模式 | [Guarded Blocks](https://docs.oracle.com/javase/tutorial/essential/concurrency/guardmeth.html) |
| ThreadLocal | 原理、内存泄漏问题 | - |
| JUC 入门 | AtomicInteger、ConcurrentHashMap | [java.util.concurrent](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/package-summary.html) |

**推荐资源**：
- [【书籍】Java 并发编程实战（Brian Goetz）](https://book.douban.com/subject/10484692/)
- [【博客】Java 并发编程 - 深入浅出](https://www.cnblogs.com/dolphin0520/category/1426288.html)

**练习**：实现一个多线程文件下载器，支持断点续传和下载进度显示。

---

### 第一阶段考核标准

| 考核项 | 达标标准 |
|---|---|
| 基础语法笔试 | 正确率 ≥ 85% |
| 集合源码理解 | 能手绘 HashMap put 流程图 |
| 多线程编程 | 能实现生产者消费者、死锁演示代码 |
| 综合项目 | 独立完成 2000+ 行控制台项目，代码结构清晰 |

---

## 第二阶段：Java 进阶技术（8-10 周）

### 学习目标
- 深入理解 JVM 内存模型与 GC 机制
- 掌握 JUC 并发工具类与线程池使用
- 熟练使用 MySQL 数据库，理解索引与事务
- 掌握反射、代理、泛型等高级特性

---

#### 2.1 JVM 深度解析（第 9-11 周）

| 学习内容 | 重点 | 资源链接 |
|---|---|---|
| JVM 内存结构 | 堆/栈/方法区/程序计数器、JDK 8 元空间变化 | [JVM Memory Management](https://docs.oracle.com/javase/specs/jvms/se17/html/jvms-2.html) |
| 类加载机制 | 双亲委派模型、破坏双亲委派、SPI 机制 | - |
| 垃圾回收 | 标记-清除/复制/标记-整理/分代回收 | [GC Tuning Guide](https://docs.oracle.com/en/java/javase/17/gctuning/) |
| GC 算法对比 | Serial/Parallel/CMS/G1/ZGC | - |
| JVM 调优 | jps/jstat/jmap/jstack、GC 日志分析 | [JVM 调优 - Arthas](https://arthas.aliyun.com/doc/) |
| 内存泄漏排查 | MAT 分析、OOM 场景复现与定位 | - |

**推荐资源**：
- [【书籍】深入理解 Java 虚拟机（周志明）](https://book.douban.com/subject/34907497/)
- [【视频】尚硅谷宋红康 JVM 全套教程](https://www.bilibili.com/video/BV1PJ411n7xZ)

**练习**：编写代码触发各种 OOM（堆/栈/方法区/直接内存），并使用 MAT/JProfiler 分析 dump 文件。

---

#### 2.2 JUC 并发编程深入（第 12-13 周）

| 学习内容 | 重点 | 资源链接 |
|---|---|---|
| Lock 体系 | ReentrantLock、AQS 原理、公平锁/非公平锁 | [Lock Objects](https://docs.oracle.com/javase/tutorial/essential/concurrency/newlocks.html) |
| 线程池 | 核心参数、四种拒绝策略、合理配置线程数 | [Executors](https://docs.oracle.com/javase/tutorial/essential/concurrency/executors.html) |
| CountDownLatch/CyclicBarrier/Semaphore | 使用场景与区别 | - |
| ConcurrentHashMap | JDK 7 分段锁 vs JDK 8 CAS+synchronized | [ConcurrentHashMap 源码分析](https://blog.csdn.net/qq_41737716/article/details/127263349) |
| CopyOnWriteArrayList | 写时复制机制、适用场景 | - |
| CompletableFuture | 异步编排、thenCombine/thenApply/exceptionally | [CompletableFuture API](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/CompletableFuture.html) |

**面试重点**：AQS 原理、线程池工作流程、ConcurrentHashMap 扩容机制。

---

#### 2.3 反射、代理与泛型（第 14 周）

| 学习内容 | 重点 | 资源链接 |
|---|---|---|
| 反射机制 | Class 对象、Field/Method/Constructor、性能优化 | [Reflection API](https://docs.oracle.com/javase/tutorial/reflect/) |
| 动态代理 | JDK 动态代理（Proxy/InvocationHandler）、CGLIB | [Dynamic Proxy Classes](https://docs.oracle.com/javase/8/docs/technotes/guides/reflection/proxy.html) |
| 泛型 | 类型擦除、通配符（? extends/? super）、泛型方法 | [Generics](https://docs.oracle.com/javase/tutorial/java/generics/) |

---

#### 2.4 MySQL 数据库（第 15-17 周）

| 学习内容 | 重点 | 资源链接 |
|---|---|---|
| SQL 基础 | 增删改查、JOIN、子查询、聚合函数 | [MySQL 8.0 官方文档](https://dev.mysql.com/doc/refman/8.0/en/) |
| 索引 | B+Tree、聚簇索引/非聚簇索引、覆盖索引、最左前缀 | [MySQL Indexes](https://dev.mysql.com/doc/refman/8.0/en/optimization-indexes.html) |
| EXPLAIN | type/rows/Extra 解读、索引优化实战 | [EXPLAIN Output Format](https://dev.mysql.com/doc/refman/8.0/en/explain-output.html) |
| 事务与锁 | ACID、MVCC、行锁/间隙锁/临键锁 | [InnoDB Locking](https://dev.mysql.com/doc/refman/8.0/en/innodb-locking.html) |
| SQL 优化 | 慢查询、分页优化、避免索引失效 | [Optimization Overview](https://dev.mysql.com/doc/refman/8.0/en/optimization.html) |
| 分库分表 | 垂直拆分/水平拆分、ShardingSphere 入门 | [ShardingSphere 官方](https://shardingsphere.apache.org/) |

**推荐资源**：
- [【书籍】高性能 MySQL（第 4 版）](https://book.douban.com/subject/35231272/)
- [【视频】尚硅谷 MySQL 高级教程](https://www.bilibili.com/video/BV1KW411u7vy)

**练习**：对一张 100 万数据的订单表进行索引设计和 SQL 优化，要求关键查询耗时 < 50ms。

---

#### 2.5 设计模式（穿插学习）

| 重点模式 | 使用场景 |
|---|---|
| 单例模式 | Spring Bean 默认作用域、数据库连接池 |
| 工厂模式 | Spring BeanFactory、MyBatis SqlSessionFactory |
| 代理模式 | Spring AOP、MyBatis Mapper 代理 |
| 观察者模式 | Spring Event、消息队列监听 |
| 策略模式 | 支付方式切换、规则引擎 |
| 模板方法模式 | Spring JdbcTemplate、RestTemplate |
| 责任链模式 | 过滤器链、Spring Security 拦截链 |

**推荐**：[【书籍】Head First 设计模式](https://book.douban.com/subject/2243615/)

---

### 第二阶段考核标准

| 考核项 | 达标标准 |
|---|---|
| JVM 调优 | 能使用 jstat/jstack 定位线上问题，设计 JVM 参数 |
| 多线程编程 | 能设计线程安全的缓存组件，合理配置线程池 |
| MySQL 优化 | 能针对慢查询进行索引优化，理解执行计划 |
| 设计模式 | 能说出 6 种以上设计模式在 Spring 中的应用 |

---

## 第三阶段：Maven 项目管理（2-3 周）

### 学习目标
- 掌握 Maven 核心生命周期与坐标体系
- 能够编写符合规范的 POM 文件
- 理解依赖传递、版本冲突与解决策略
- 掌握多模块项目构建与私服配置

---

#### 3.1 Maven 核心概念（第 1 周）

| 学习内容 | 重点 | 资源链接 |
|---|---|---|
| Maven 安装与配置 | settings.xml 配置、镜像仓库配置 | [Maven 下载](https://maven.apache.org/download.cgi) |
| 项目坐标 | groupId/artifactId/version 命名规范 | [Maven Coordinates](https://maven.apache.org/pom.html#Maven_Coordinates) |
| 依赖管理 | scope（compile/provided/runtime/test）、optional | [Dependency Mechanism](https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html) |
| 生命周期 | clean/default/site、常用插件绑定 | [Lifecycle Reference](https://maven.apache.org/guides/introduction/introduction-to-the-lifecycle.html) |
| POM 继承与聚合 | parent、modules、dependencyManagement | [POM Reference](https://maven.apache.org/pom.html) |

**推荐**：
- [【书籍】Maven 实战（许晓斌）](https://book.douban.com/subject/5346682/)
- [【官方】Maven 入门指南](https://maven.apache.org/guides/getting-started/)

---

#### 3.2 依赖管理与冲突解决（第 2 周）

| 学习内容 | 重点 |
|---|---|
| 依赖传递 | 最短路径优先、第一声明优先 |
| 依赖冲突 | `mvn dependency:tree` 分析、exclusion 排除 |
| 版本统一 | dependencyManagement 集中管理 |
| BOM | Spring Boot BOM、三方 BOM 引入 |

**练习**：
1. 在三方依赖冲突场景下使用 `mvn dependency:tree` 分析并解决冲突
2. 在项目中使用 exclusion 排除传递依赖中的特定版本

---

#### 3.3 多模块与私服（第 3 周）

| 学习内容 | 重点 |
|---|---|
| 多模块项目 | 模块拆分原则、依赖关系设计 |
| 自定义 Archetype | 团队脚手架快速搭建 |
| 私服搭建 | Nexus/JFrog Artifactory 安装与配置 |
| 发布管理 | deploy 到私服、SNAPSHOT vs RELEASE |

**实战案例**：将一个传统的单体项目拆分为多模块 Maven 项目，结构为：

```
ecommerce-platform/
├── pom.xml                    (父 POM)
├── ecommerce-common/          (公共模块)
├── ecommerce-dao/             (数据访问层)
├── ecommerce-service/         (业务逻辑层)
├── ecommerce-web/             (Web 层)
└── ecommerce-api/             (对外接口)
```

---

### 第三阶段考核标准

| 考核项 | 达标标准 |
|---|---|
| POM 编写 | 能独立编写多模块 POM 文件，正确管理依赖 |
| 依赖冲突 | 能使用 dependency:tree 分析并解决至少 3 种冲突场景 |
| 多模块构建 | 能搭建 3+ 模块的项目结构并成功构建 |

---

## 第四阶段：Spring Boot 框架应用（8-10 周）

### 学习目标
- 掌握 Spring Boot 核心原理与自动配置
- 熟练使用 Spring MVC、MyBatis-Plus 进行 Web 开发
- 掌握 Spring Security 认证鉴权体系
- 理解 Spring 事务管理与 AOP 原理
- 能够独立完成 Restful API 设计与开发

---

#### 4.1 Spring 核心基础（第 1-2 周）

| 学习内容 | 重点 | 资源链接 |
|---|---|---|
| IoC 容器 | BeanFactory/ApplicationContext、依赖注入方式 | [Spring IoC Container](https://docs.spring.io/spring-framework/reference/core/beans.html) |
| Bean 生命周期 | 实例化→属性填充→初始化→销毁，BeanPostProcessor | [Bean Lifecycle](https://docs.spring.io/spring-framework/reference/core/beans/factory-nature.html) |
| 依赖注入 | @Autowired/@Qualifier/@Resource、循环依赖与三级缓存 | [Dependency Injection](https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html) |
| 配置方式 | XML/注解/Java Config、@Configuration/@Bean | [Java-based Container Configuration](https://docs.spring.io/spring-framework/reference/core/beans/java.html) |

**面试重点**：Spring 如何解决循环依赖（三级缓存机制）。

---

#### 4.2 Spring Boot 快速入门（第 3-4 周）

| 学习内容 | 重点 | 资源链接 |
|---|---|---|
| 自动配置原理 | @SpringBootApplication、@EnableAutoConfiguration、spring.factories | [Auto-configuration](https://docs.spring.io/spring-boot/reference/features/developing-auto-configuration.html) |
| 起步依赖 | spring-boot-starter-web/data/security 等 | [Spring Boot Starters](https://docs.spring.io/spring-boot/reference/using/build-systems.html#using.build-systems.starters) |
| 配置文件 | application.yml、多环境配置、@ConfigurationProperties | [External Config](https://docs.spring.io/spring-boot/reference/features/external-config.html) |
| 日志框架 | SLF4J + Logback、日志级别、logback-spring.xml | [Logging](https://docs.spring.io/spring-boot/reference/features/logging.html) |
| Actuator | 健康检查、metrics、info 端点 | [Spring Boot Actuator](https://docs.spring.io/spring-boot/reference/actuator/index.html) |

**推荐资源**：
- [【官方】Spring Boot Reference Documentation](https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/)
- [【视频】尚硅谷雷丰阳 Spring Boot 2](https://www.bilibili.com/video/BV19K4y1L7MT)

**练习**：从零搭建一个 Spring Boot 项目，集成 Actuator + 自定义健康检查指标。

---

#### 4.3 Spring MVC 与 RESTful API（第 5-6 周）

| 学习内容 | 重点 | 资源链接 |
|---|---|---|
| 请求映射 | @RequestMapping/@GetMapping/@PostMapping | [Spring MVC](https://docs.spring.io/spring-framework/reference/web/webmvc.html) |
| 参数绑定 | @RequestParam/@PathVariable/@RequestBody | - |
| 数据校验 | @Valid + JSR-303 注解、全局异常处理器 | [Validation](https://docs.spring.io/spring-framework/reference/core/validation/beanvalidation.html) |
| 统一响应 | 统一返回体设计（code/message/data） | - |
| 拦截器与过滤器 | HandlerInterceptor vs Filter、执行顺序 | [Interceptors](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-config/interceptors.html) |
| 跨域处理 | @CrossOrigin、CorsFilter | [CORS Support](https://docs.spring.io/spring-framework/reference/web/webmvc-cors.html) |
| 文件上传/下载 | MultipartFile、大文件分片上传 | - |

**实战**：设计并实现一套标准的 RESTful API，包含统一响应格式、全局异常处理、参数校验。

---

#### 4.4 MyBatis-Plus 与数据访问（第 7 周）

| 学习内容 | 重点 | 资源链接 |
|---|---|---|
| MyBatis 基础 | XML 映射、动态 SQL、ResultMap | [MyBatis 官方文档](https://mybatis.org/mybatis-3/zh/) |
| MyBatis-Plus | 通用 CRUD、条件构造器、分页插件 | [MyBatis-Plus 官方文档](https://baomidou.com/) |
| 代码生成器 | 自动生成 Entity/Mapper/Service/Controller | - |
| 多数据源 | dynamic-datasource、读写分离 | [dynamic-datasource](https://github.com/baomidou/dynamic-datasource-spring-boot-starter) |

---

#### 4.5 Spring 事务管理（第 8 周）

| 学习内容 | 重点 |
|---|---|
| 声明式事务 | @Transactional、rollbackFor、propagation |
| 事务传播行为 | REQUIRED/REQUIRES_NEW/NESTED |
| 事务失效场景 | 自调用、非 public 方法、异常被捕获 |

**面试重点**：说出 5 种以上 @Transactional 失效场景。

---

#### 4.6 Spring Security 认证鉴权（第 9 周）

| 学习内容 | 重点 | 资源链接 |
|---|---|---|
| 认证流程 | UsernamePasswordAuthenticationFilter 链路 | [Spring Security Architecture](https://docs.spring.io/spring-security/reference/servlet/architecture.html) |
| JWT 集成 | Token 生成/验证/刷新、无状态认证 | - |
| 权限控制 | @PreAuthorize、RBAC 模型、动态权限 | [Authorization](https://docs.spring.io/spring-security/reference/servlet/authorization/index.html) |

---

#### 4.7 中间件集成（第 10 周）

| 学习内容 | 重点 | 资源链接 |
|---|---|---|
| Redis | Spring Cache + Redis、分布式锁（Redisson） | [Redis 官方文档](https://redis.io/docs/latest/) |
| RabbitMQ | 消息发送与消费、死信队列、延迟队列 | [RabbitMQ 官方](https://www.rabbitmq.com/docs) |

---

#### 第四阶段实战案例：电商订单模块

```
├── 用户认证（Spring Security + JWT）
├── 商品管理（CRUD + 分页 + 条件查询）
├── 订单管理（创建/支付/取消/查询）
├── 购物车（Redis 缓存）
├── 全局异常处理
├── 参数校验
├── 统一返回体
└── API 文档（Knife4j / SpringDoc）
```

---

### 第四阶段考核标准

| 考核项 | 达标标准 |
|---|---|
| Spring Boot 项目搭建 | 10 分钟内完成新项目初始化与基础配置 |
| RESTful API 设计 | 能设计规范的 API 并编写接口文档 |
| 事务管理 | 能解释 5 种以上事务失效场景及解决方案 |
| 电商模块实战 | 独立完成 4+ 接口的订单模块，含认证鉴权 |

---

## 第五阶段：综合实战项目（6-8 周）

### 电商平台综合项目

将前面所学技术栈整合，完成一个完整的电商平台后端项目。

#### 技术栈

| 类别 | 技术选型 |
|---|---|
| 框架 | Spring Boot 3.x |
| 数据访问 | MyBatis-Plus + MySQL 8.0 |
| 缓存 | Redis（Redisson 分布式锁） |
| 消息队列 | RabbitMQ |
| 认证鉴权 | Spring Security + JWT |
| API 文档 | Knife4j |
| 构建工具 | Maven 多模块 |
| 部署 | Docker + Docker Compose |

#### 核心模块

| 模块 | 功能点 |
|---|---|
| 用户服务 | 注册、登录、JWT 认证、角色权限 |
| 商品服务 | 商品 CRUD、分类管理、库存扣减 |
| 订单服务 | 创建订单、订单状态流转、超时取消（延迟队列） |
| 购物车 | Redis 实现、离线合并 |
| 秒杀模块 | 预扣库存、Redis + Lua 防超卖、限流 |

#### P6 级关键考察点

| 考察点 | 要求 |
|---|---|
| 库存防超卖 | 乐观锁 / Redis Lua 脚本 / 分布式锁 |
| 订单号生成 | 雪花算法 / 号段模式 |
| 缓存设计 | 缓存预热、缓存穿透/击穿/雪崩处理 |
| 接口幂等 | Token 机制 / 数据库唯一索引 |
| 异常处理 | 全局异常拦截 + 统一错误码 |
| 日志规范 | 关键操作日志 + 链路追踪 ID |

---

## 学习方法建议

### 1. 费曼学习法
学完一个知识点后，尝试用自己的话讲给别人听。如果不能清晰表达，说明理解还不够深入。

### 2. 输出驱动输入
- 每学完一个模块写一篇技术博客（CSDN/掘金/个人博客）
- 画思维导图整理知识体系
- 开源自己的代码到 GitHub

### 3. 源码阅读方法论
- **第一遍**：理解整体流程，忽略细节
- **第二遍**：断点调试，跟踪核心流程
- **第三遍**：画时序图/流程图，输出笔记

### 4. 面试准备策略
- 刷题：[LeetCode Hot 100](https://leetcode.cn/problem-list/2cktkvj/) + [剑指 Offer](https://leetcode.cn/problem-list/xb9nqhhg/)
- 八股文：建立知识体系而不是死记硬背
- 项目描述：STAR 法则（情境→任务→行动→结果）

### 5. 每日时间分配建议（全日制）

| 时间段 | 内容 |
|---|---|
| 上午（3h） | 新知识学习（视频/书籍） |
| 下午（3h） | 编码练习 + 项目实战 |
| 晚上（2h） | 复习 + 笔记整理 + 算法刷题 |

---

## 常见问题与解决方案

### Q1：学完就忘怎么办？

> **方案**：使用间隔重复法（Anki 闪卡）、定期复习。每周末花 2 小时回顾本周内容，每月花 1 天回顾本月内容。

### Q2：遇到 Bug 卡住很久？

> **方案**：
> 1. 先阅读错误日志完整信息
> 2. Google/Stack Overflow 搜索
> 3. ChatGPT/Claude 辅助分析
> 4. 如果超过 30 分钟未解决，先跳过，第二天再看

### Q3：学完基础后不知道做什么项目？

> **方案**：从模仿开始——
> 1. 仿写一个简易版 Spring（IoC + AOP）
> 2. 仿写一个 Tomcat（Socket + 线程池）
> 3. 仿写一个 RPC 框架（Netty + 注册中心）
> 4. 仿写一个 ORM 框架（JDBC + 反射 + 注解）

### Q4：如何判断自己是否达到 P6 水平？

> **自检清单**：
> - 能独立负责一个微服务模块的设计与开发
> - 能看懂主流框架核心源码（Spring IoC/AOP、MyBatis）
> - 能进行 JVM 调优和 SQL 优化
> - 能写出高质量的技术方案文档
> - LeetCode 中等难度题目通过率 > 70%
> - 有完整的项目经验（含上线部署）

---

## P6 面试能力清单

| 能力维度 | 具体要求 |
|---|---|
| Java 基础 | JVM、并发编程、集合框架源码、IO 模型 |
| 框架能力 | Spring Boot 自动配置、事务管理、AOP 原理 |
| 数据库 | MySQL 索引与优化、事务与锁、分库分表 |
| 中间件 | Redis 数据结构与高可用、消息队列 |
| 系统设计 | 接口幂等、分布式 ID、限流/熔断/降级 |
| 编码能力 | 算法与数据结构、设计模式 |
| 工程能力 | CI/CD、Docker、单元测试、代码规范 |
| 软技能 | 技术方案评审、指导新人、跨团队协作 |

---

> **最后提醒**：技术学习是一场马拉松而非百米冲刺。保持好奇心与持续学习的习惯，比任何知识点都更重要。祝你早日成为优秀的 Java 工程师！