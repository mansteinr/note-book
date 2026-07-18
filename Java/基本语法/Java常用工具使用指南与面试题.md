# Java 常用工具使用指南与面试题

## 目录

- [一、Lombok —— 消除样板代码](#一lombok--消除样板代码)
- [二、SLF4J / Logback —— 日志框架](#二slf4j--logback--日志框架)
- [三、Guava —— Google 核心工具库](#三guava--google-核心工具库)
- [四、Apache Commons 系列](#四apache-commons-系列)
  - [4.1 Commons Lang3](#41-commons-lang3)
  - [4.2 Commons Collections4](#42-commons-collections4)
  - [4.3 Commons IO](#43-commons-io)
- [五、Jackson —— JSON 处理](#五jackson--json-处理)
- [六、Mockito —— 单元测试 Mock 框架](#六mockito--单元测试-mock-框架)
- [七、Hutool —— 国产 Java 工具集](#七hutool--国产-java-工具集)
- [八、JUnit 5 —— 测试框架](#八junit-5--测试框架)

---

## 一、Lombok —— 消除样板代码

### 1.1 工具简介

Lombok 是一个 Java 库，通过注解在编译时自动生成 getter/setter、构造方法、toString、equals/hashCode 等样板代码，使代码更加简洁。

**核心原理：** Lombok 基于 JSR 269（Pluggable Annotation Processing API），在编译阶段操作 AST（抽象语法树），向字节码中注入对应的方法实现。

**Maven 依赖：**

```xml
<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <version>1.18.36</version>
    <scope>provided</scope>
</dependency>
```

### 1.2 核心功能说明

| 注解 | 功能 | 生成内容 |
|------|------|----------|
| `@Getter` / `@Setter` | 生成 getter/setter 方法 | 类或字段级别 |
| `@ToString` | 生成 toString() 方法 | 可排除字段、包含父类 |
| `@EqualsAndHashCode` | 生成 equals() 和 hashCode() | 可排除字段、调用父类方法 |
| `@NoArgsConstructor` | 生成无参构造方法 | 可选强制字段 final 初始化 |
| `@AllArgsConstructor` | 生成全参构造方法 | 包含所有字段 |
| `@RequiredArgsConstructor` | 生成必要参数的构造方法 | 只包含 final 或 @NonNull 字段 |
| `@Data` | 组合注解 | @Getter + @Setter + @ToString + @EqualsAndHashCode + @RequiredArgsConstructor |
| `@Builder` | 生成建造者模式代码 | 创建内部 Builder 类 |
| `@Slf4j` / `@Log4j2` | 注入日志对象 | 自动创建 log 常量 |
| `@Value` | 不可变类 | 生成 final 字段、全参构造、getter、equals/hashCode/toString |

### 1.3 基础使用示例

```java
import lombok.*;

// 使用 @Data 组合注解，等价于同时使用 @Getter @Setter @ToString @EqualsAndHashCode @RequiredArgsConstructor
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {
    private Long id;
    private String username;
    private String email;
    private Integer age;
}

// 使用示例
public class LombokDemo {
    public static void main(String[] args) {
        // 使用 @Builder 建造者模式创建对象
        User user = User.builder()
                .id(1L)
                .username("张三")
                .email("zhangsan@example.com")
                .age(25)
                .build();

        // 使用 @Getter 生成的 getter 方法
        System.out.println(user.getUsername()); // 输出: 张三

        // 使用 @Setter 生成的 setter 方法
        user.setAge(26);

        // 使用 @ToString 生成的 toString 方法
        System.out.println(user); // 输出: User(id=1, username=张三, email=zhangsan@example.com, age=26)
    }
}
```

### 1.4 高级特性

**@Builder.Default —— 设置构建器默认值：**

```java
@Builder
public class Config {
    private String host;

    @Builder.Default
    private int port = 8080; // 构建时如不指定则使用默认值 8080

    @Builder.Default
    private int timeout = 3000;
}
```

**@Singular —— 集合字段的构建器模式：**

```java
@Builder
public class Department {
    private String name;

    @Singular
    private List<String> members;

    @Singular("tag")
    private Set<String> tags;
}

// 使用示例
Department dept = Department.builder()
        .name("开发部")
        .member("张三")
        .member("李四")
        .member("王五")   // 多次调用自动收集到 List
        .tag("backend")
        .tag("java")
        .build();
```

**@Accessors —— 链式调用风格：**

```java
@Data
@Accessors(chain = true) // 启用链式调用
public class ChainDemo {
    private String name;
    private int age;
}

// 使用示例：setter 返回 this 支持链式调用
ChainDemo demo = new ChainDemo()
        .setName("李四")
        .setAge(30);
```

### 1.5 注意事项

1. **IDE 插件配合：** 必须在 IDE 中安装 Lombok 插件，否则编译器会报"找不到方法"的错误。
2. **@Data 慎用于 JPA 实体：** @Data 生成的 equals/hashCode 包含所有字段，JPA 实体中应使用仅包含主键的 @EqualsAndHashCode。
3. **@Builder 与继承：** 父类字段无法通过子类的 @Builder 直接设置，需要手动编写构造方法或在父类也使用 @Builder。
4. **@ToString 循环引用：** 双向关联的实体使用 @ToString 可能造成 StackOverflowError，需使用 `@ToString.Exclude` 排除关联字段。
5. **版本兼容性：** JDK 版本升级时需同步升级 Lombok 版本，如 JDK 21 需要 Lombok 1.18.30+。

### 1.6 常见问题解答

**Q1: Lombok 会影响性能吗？**
Lombok 在编译期生成代码，运行时没有额外开销，不会影响性能。

**Q2: 为什么使用了 @Data 后 @Builder 会报错？**
@Data 包含 @RequiredArgsConstructor，与 @Builder 的 @AllArgsConstructor 冲突。需要手动添加 @NoArgsConstructor 和 @AllArgsConstructor。

**Q3: 多模块项目中 Lombok 不生效？**
确保每个子模块都添加了 Lombok 依赖，或者通过 `<dependencyManagement>` 统一管理版本。

### 1.7 面试题

**Q1: 请简述 Lombok 的实现原理。**

Lombok 基于 JSR 269 插入式注解处理 API，在编译阶段（javac）操作 AST（抽象语法树）。具体流程：
1. javac 编译源码生成 AST
2. Lombok 注解处理器扫描带有 Lombok 注解的节点
3. Lombok 直接修改 AST，向其中注入对应的方法节点（如 getter/setter 方法）
4. javac 基于修改后的 AST 生成字节码

由于整个过程在编译期完成，运行时没有任何额外开销。

**Q2: @Data 和 @Value 的区别是什么？**

| 对比维度 | @Data | @Value |
|---------|-------|--------|
| 类类型 | 可变类 | 不可变类 |
| 字段修饰 | 非 final | 自动加 final |
| 生成 setter | 有 | 无 |
| 生成构造方法 | @RequiredArgsConstructor | @AllArgsConstructor |
| 用途 | 普通 POJO | 值对象、DTO |

**Q3: @Builder 模式在继承场景下如何使用？**

```java
@Getter
@SuperBuilder
@NoArgsConstructor
public class Parent {
    private String parentField;
}

@Getter
@SuperBuilder
@NoArgsConstructor
public class Child extends Parent {
    private String childField;
}

// 使用
Child child = Child.builder()
        .parentField("parent") // 可以设置父类字段
        .childField("child")
        .build();
```

使用 `@SuperBuilder` 替代 `@Builder` 即可在继承场景下使用建造者模式。

**Q4: Lombok 的 @Slf4j 是如何注入日志对象的？**

@Slf4j 在编译时会自动生成如下代码：

```java
// 编译前
@Slf4j
public class MyService {
    public void doSomething() {
        log.info("doing something");
    }
}

// 编译后等价于
public class MyService {
    private static final org.slf4j.Logger log = 
        org.slf4j.LoggerFactory.getLogger(MyService.class);
    
    public void doSomething() {
        log.info("doing something");
    }
}
```

**Q5: 使用 Lombok 需要注意哪些坑？**

1. **@EqualsAndHashCode 在继承时：** 默认 `callSuper = false`，不会调用父类方法，可能导致 equals 比较不全。
2. **@ToString 循环引用：** 双向关系（如订单→订单明细→订单）会导致 StackOverflowError。
3. **@Builder 默认值：** 未使用 @Builder.Default 时，字段初始值会被忽略。
4. **@Data 与 JPA 懒加载：** 代理对象的 equals/hashCode 可能出错。
5. **实体类序列化：** 使用 @Data 的实体类在 JSON 序列化时可能暴露所有字段。

---

## 二、SLF4J / Logback —— 日志框架

### 2.1 工具简介

SLF4J（Simple Logging Facade for Java）是 Java 日志门面，为各种日志框架（Logback、Log4j2、JUL 等）提供统一接口。Logback 是 SLF4J 的原生实现，也是 Spring Boot 默认的日志框架。

**架构分层：**

```
应用代码 → SLF4J（门面） → Logback/Log4j2（实现）
```

**Maven 依赖：**

```xml
<!-- SLF4J 门面 -->
<dependency>
    <groupId>org.slf4j</groupId>
    <artifactId>slf4j-api</artifactId>
    <version>2.0.16</version>
</dependency>
<!-- Logback 实现 -->
<dependency>
    <groupId>ch.qos.logback</groupId>
    <artifactId>logback-classic</artifactId>
    <version>1.5.12</version>
</dependency>
```

### 2.2 核心功能说明

| 功能 | 说明 |
|------|------|
| 日志级别 | TRACE < DEBUG < INFO < WARN < ERROR，支持动态调整 |
| 占位符 | 使用 `{}` 占位符，避免字符串拼接开销 |
| 参数化日志 | 支持可变参数，自动格式化 |
| MDC | Mapped Diagnostic Context，支持多线程上下文传递 |
| Marker | 日志标记，用于分类和过滤 |
| 配置热加载 | `scan=true` 支持配置文件热更新 |

### 2.3 基础使用示例

**logback-spring.xml 配置：**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration scan="true" scanPeriod="60 seconds">
    <!-- 定义日志输出格式 -->
    <property name="LOG_PATTERN" 
              value="%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n"/>

    <!-- 控制台输出 -->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>${LOG_PATTERN}</pattern>
            <charset>UTF-8</charset>
        </encoder>
    </appender>

    <!-- 文件输出：按天滚动 -->
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>logs/app.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>logs/app.%d{yyyy-MM-dd}.log</fileNamePattern>
            <maxHistory>30</maxHistory> <!-- 保留 30 天 -->
        </rollingPolicy>
        <encoder>
            <pattern>${LOG_PATTERN}</pattern>
        </encoder>
    </appender>

    <!-- 不同包设置不同级别 -->
    <logger name="com.example.dao" level="DEBUG"/>
    <logger name="org.springframework" level="WARN"/>

    <!-- 根日志级别 -->
    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="FILE"/>
    </root>
</configuration>
```

**Java 代码使用：**

```java
import lombok.extern.slf4j.Slf4j;

@Slf4j  // Lombok 自动注入 log 对象
public class LogbackDemo {
    public static void main(String[] args) {
        String username = "张三";
        int orderId = 10086;

        // 使用 {} 占位符，自动拼接，避免不必要的字符串操作
        log.info("用户 {} 创建了订单，订单号: {}", username, orderId);

        // 异常日志：最后一个参数传异常对象，自动打印堆栈
        try {
            int result = 10 / 0;
        } catch (Exception e) {
            log.error("计算发生异常", e);
        }

        // 调试日志
        log.debug("调试信息: 当前用户={}", username);
    }
}
```

### 2.4 高级特性

**MDC 实现全链路追踪：**

```java
import org.slf4j.MDC;

// 在拦截器或过滤器中设置 traceId
@Slf4j
public class TraceInterceptor implements HandlerInterceptor {
    @Override
    public boolean preHandle(HttpServletRequest request, 
                             HttpServletResponse response, Object handler) {
        // 将 traceId 放入 MDC，该请求的所有日志都会携带此标识
        MDC.put("traceId", UUID.randomUUID().toString().replace("-", ""));
        return true;
    }

    @Override
    public void afterCompletion(HttpServletRequest request, 
                                HttpServletResponse response, Object handler, Exception ex) {
        // 请求结束后必须清除 MDC，防止内存泄漏
        MDC.clear();
    }
}

// 在 logback 配置中使用 %X{traceId} 输出 traceId
// <pattern>%d{yyyy-MM-dd HH:mm:ss} [%thread] [%X{traceId}] %-5level %logger - %msg%n</pattern>
```

**异步日志（提升性能）：**

```xml
<!-- 使用 AsyncAppender 包装实际 Appender -->
<appender name="ASYNC_FILE" class="ch.qos.logback.classic.AsyncAppender">
    <queueSize>512</queueSize>           <!-- 队列大小 -->
    <discardingThreshold>0</discardingThreshold> <!-- 不丢弃日志 -->
    <appender-ref ref="FILE"/>
</appender>
```

### 2.5 注意事项

1. **日志级别选择：** DEBUG 用于开发调试，INFO 记录关键业务流程，WARN 记录潜在问题，ERROR 记录需要人工介入的异常。
2. **避免使用字符串拼接：** 使用 `log.debug("user={}", user)` 而非 `log.debug("user=" + user)`，前者在 DEBUG 级别关闭时不会执行字符串拼接。
3. **异常日志规范：** 使用 `log.error("msg", exception)` 传递异常，不要使用 `e.getMessage()` 或 `e.toString()`。
4. **MDC 使用后清理：** 线程池场景下务必在 finally 中调用 `MDC.clear()`，否则会污染其他线程。
5. **避免日志打印敏感信息：** 手机号、身份证、密码等敏感信息需要脱敏处理。

### 2.6 常见问题解答

**Q1: SLF4J 和 Logback、Log4j2 是什么关系？**
SLF4J 是门面（接口），Logback 和 Log4j2 是实现。代码中只依赖 SLF4J 接口，切换日志实现只需更换依赖包，无需修改代码。

**Q2: 日志文件过大如何管理？**
使用 RollingFileAppender + TimeBasedRollingPolicy 按天分割，或 SizeBasedTriggeringPolicy 按文件大小分割。

### 2.7 面试题

**Q1: 请简述 SLF4J 的门面模式及其优势。**

SLF4J 使用门面模式（Facade Pattern），只提供日志接口，由具体实现框架（Logback、Log4j2）完成实际日志输出。优势：
1. **解耦：** 应用代码无需关心底层实现
2. **灵活切换：** 替换日志框架只需更换依赖，无需修改代码
3. **统一管理：** 项目中可能引入多个第三方库，它们各自使用不同日志框架，SLF4J 提供桥接器统一输出

**Q2: 日志级别从低到高排列，以及各自的使用场景？**

`TRACE < DEBUG < INFO < WARN < ERROR`

- **TRACE：** 最细粒度的追踪信息，一般用于深入排查问题
- **DEBUG：** 开发调试信息，记录变量值、方法调用等
- **INFO：** 关键业务流程节点，如用户登录、订单创建、服务启动
- **WARN：** 潜在问题，不影响当前功能但需关注，如配置缺失使用默认值
- **ERROR：** 错误异常，需要人工介入处理，如数据库连接失败

**Q3: 为什么推荐使用 `log.info("{}", obj)` 而不是 `log.info(obj.toString())`？**

1. **性能优化：** 当该日志级别关闭时，`{}` 占位符方式不会执行参数拼接，而 `toString()` 会被调用产生不必要的开销。
2. **避免 NPE：** 占位符方式如果 obj 为 null，只会输出 "null"；而手动调用 `obj.toString()` 会抛出 NullPointerException。
3. **代码简洁：** 占位符方式更简洁，可读性更好。

**Q4: MDC 的实现原理是什么？它在多线程环境下如何传递？**

MDC 底层基于 ThreadLocal 实现，每个线程持有独立的 Map 副本：

```java
public class MDC {
    // 实际存储在每个线程的 ThreadLocal 中
    static final ThreadLocal<Map<String, String>> mdcAdapter = new ThreadLocal<>();
}
```

在多线程/线程池场景下，MDC 不会自动传递。解决方案：
1. **手动传递：** `MDC.getCopyOfContextMap()` 获取父线程 MDC，子线程中 `MDC.setContextMap()`
2. **使用 SLF4J 的 MDC 增强工具：** 如 `logback-mdc-extension`
3. **使用 TransmittableThreadLocal（TTL）：** 阿里开源的 TTL 可在线程池中传递 ThreadLocal 值

**Q5: 如何设计一个日志脱敏方案？**

核心思路：自定义 `MessageConverter` 或 `Layout`，在日志输出前对敏感信息进行处理。

```java
// 自定义转换器
public class SensitiveConverter extends MessageConverter {
    @Override
    public String convert(ILoggingEvent event) {
        String message = super.convert(event);
        // 手机号脱敏：138****5678
        message = message.replaceAll("(1[3-9]\\d)\\d{4}(\\d{4})", "$1****$2");
        // 身份证脱敏：110***********1234
        message = message.replaceAll("(\\d{3})\\d{11}(\\w{4})", "$1***********$2");
        return message;
    }
}
```

**Q6: 异步日志的原理和优缺点？**

**原理：** AsyncAppender 使用一个阻塞队列（BlockingQueue）作为缓冲区，业务线程将日志事件放入队列即返回，后台线程异步消费队列写入磁盘。

**优点：**
- 避免日志 IO 阻塞业务线程，提升应用吞吐量
- 削峰填谷，应对突发大量日志

**缺点：**
- 应用崩溃时可能丢失队列中未刷新的日志
- 增加了内存开销（队列占用堆内存）
- 日志顺序可能不严格一致

---

## 三、Guava —— Google 核心工具库

### 3.1 工具简介

Guava 是 Google 开源的 Java 核心工具库，包含集合处理、缓存、并发、字符串处理、I/O 等多个模块，是 JDK 标准库的有力补充。

**Maven 依赖：**

```xml
<dependency>
    <groupId>com.google.guava</groupId>
    <artifactId>guava</artifactId>
    <version>33.4.0-jre</version>
</dependency>
```

### 3.2 核心功能说明

| 模块 | 核心类 | 说明 |
|------|--------|------|
| 集合工具 | Lists, Sets, Maps | 快速创建集合、不可变集合 |
| 不可变集合 | ImmutableList, ImmutableSet, ImmutableMap | 线程安全的不可变集合 |
| 新型集合 | Multiset, Multimap, BiMap, Table | 增强集合类型 |
| 字符串处理 | Strings, Joiner, Splitter, CharMatcher | 字符串连接、分割、匹配 |
| 缓存 | Cache, LoadingCache | 本地缓存实现 |
| 并发 | ListenableFuture, MoreExecutors | 增强并发工具 |
| 前置条件 | Preconditions | 参数校验 |
| 事件总线 | EventBus | 进程内事件发布订阅 |
| 布隆过滤器 | BloomFilter | 大数据量去重判断 |

### 3.3 基础使用示例

**集合创建与操作：**

```java
import com.google.common.collect.*;

// 快速创建集合（JDK 9+ 也可用 List.of()）
List<String> list = Lists.newArrayList("a", "b", "c");
Set<Integer> set = Sets.newHashSet(1, 2, 3);
Map<String, Integer> map = ImmutableMap.of("key1", 1, "key2", 2);

// List 分区：将大集合按每 100 个一组分割
List<Integer> bigList = IntStream.rangeClosed(1, 250).boxed().collect(Collectors.toList());
List<List<Integer>> partitions = Lists.partition(bigList, 100);
System.out.println("分区数: " + partitions.size()); // 输出: 分区数: 3
```

**字符串操作：**

```java
import com.google.common.base.Joiner;
import com.google.common.base.Splitter;

// Joiner：连接字符串
List<String> names = Arrays.asList("张三", "李四", "王五");
String joined = Joiner.on(", ").skipNulls().join(names);
System.out.println(joined); // 输出: 张三, 李四, 王五

// Splitter：分割字符串
String input = "apple, banana, , orange";
List<String> result = Splitter.on(",")
        .trimResults()       // 去除每个元素前后空格
        .omitEmptyStrings()  // 忽略空元素
        .splitToList(input); // 结果: [apple, banana, orange]
```

### 3.4 高级特性

**Multimap —— 一个键映射多个值：**

```java
Multimap<String, String> multimap = ArrayListMultimap.create();
multimap.put("开发部", "张三");
multimap.put("开发部", "李四");
multimap.put("测试部", "王五");

Collection<String> devMembers = multimap.get("开发部");
System.out.println(devMembers); // 输出: [张三, 李四]
```

**Table —— 双键 Map（行+列）：**

```java
Table<String, String, Integer> table = HashBasedTable.create();
table.put("张三", "语文", 90);
table.put("张三", "数学", 85);
table.put("李四", "语文", 88);

System.out.println(table.get("张三", "语文")); // 输出: 90
System.out.println(table.row("张三"));         // 输出: {语文=90, 数学=85}
```

**LoadingCache —— 本地缓存：**

```java
import com.google.common.cache.*;

// 构建一个自动加载的本地缓存
LoadingCache<Long, String> userCache = CacheBuilder.newBuilder()
        .maximumSize(1000)                    // 最大缓存条目数
        .expireAfterWrite(10, TimeUnit.MINUTES) // 写入后 10 分钟过期
        .recordStats()                         // 开启统计
        .build(new CacheLoader<Long, String>() {
            @Override
            public String load(Long userId) {
                // 缓存未命中时，从此方法加载数据
                return loadFromDB(userId);
            }
        });

// 使用
String userName = userCache.get(1L); // 首次调用触发 loadFromDB
String userName2 = userCache.get(1L); // 命中缓存，直接返回

// 获取缓存统计
CacheStats stats = userCache.stats();
System.out.println("命中率: " + stats.hitRate());
```

**BloomFilter —— 布隆过滤器：**

```java
import com.google.common.hash.BloomFilter;
import com.google.common.hash.Funnels;

// 创建布隆过滤器：预计插入 100 万条数据，误判率 0.01
BloomFilter<Long> bloomFilter = BloomFilter.create(
        Funnels.longFunnel(),
        1_000_000,
        0.01
);

// 添加元素
bloomFilter.put(100L);
bloomFilter.put(200L);

// 判断是否存在
System.out.println(bloomFilter.mightContain(100L)); // true（一定准确）
System.out.println(bloomFilter.mightContain(300L)); // false（可能误判，但不会漏判）
```

### 3.5 注意事项

1. **不可变集合：** Guava 的 Immutable 集合真正不可修改，比 `Collections.unmodifiableXXX` 更安全（后者底层集合仍可变）。
2. **Cache 不是分布式缓存：** Guava Cache 是进程内缓存，不适用于分布式场景，应使用 Redis 等替代。
3. **EventBus 默认同步：** EventBus 默认在同一线程执行，需使用 AsyncEventBus 实现异步。
4. **ListenableFuture 已过期：** JDK 8+ 的 CompletableFuture 是更推荐的选择，Guava 的 ListenableFuture 已标记为 @Beta。
5. **内存占用：** BloomFilter 需要预估数据量，设置过小会导致误判率急剧上升。

### 3.6 常见问题解答

**Q1: Guava Cache 和 Redis 有什么区别？**
Guava Cache 是进程内缓存，数据存储在 JVM 堆内存中，访问速度极快但容量受限；Redis 是分布式缓存，独立部署，支持持久化和集群，适合多实例共享数据。

**Q2: 为什么 Guava 推荐使用不可变集合？**
不可变集合线程安全、内存效率高、可被安全地用作常量，并且天然防止数据被意外修改。

### 3.7 面试题

**Q1: Guava 的 LoadingCache 和普通 Map 有什么区别？**

| 对比维度 | LoadingCache | HashMap |
|---------|-------------|---------|
| 自动加载 | 缓存未命中时自动调用 load() 方法加载 | 需手动判空并加载 |
| 过期策略 | 支持按时间、大小、引用等自动过期 | 需手动清理 |
| 并发安全 | 内置分段锁，高并发场景性能好 | 需使用 ConcurrentHashMap |
| 统计信息 | 支持命中率、加载时间等统计 | 无 |
| 淘汰策略 | 支持 LRU、LFU 等 | 需手动实现 |

**Q2: 布隆过滤器的原理和应用场景？**

**原理：** 使用多个哈希函数将元素映射到位数组的多个位置。插入时将这些位置置为 1；查询时检查这些位置是否都为 1，若是则"可能存在"，若有一个为 0 则"一定不存在"。

**特性：** 有误判率（不存在的数据可能被判为存在），但不会漏判（存在的数据一定会被判为存在）。

**应用场景：**
1. 缓存穿透防护：判断请求 key 是否可能存在于数据库
2. 垃圾邮件过滤：快速判断邮件地址是否在黑名单
3. 爬虫 URL 去重：判断 URL 是否已被爬取

**Q3: Multimap 和 `Map<String, List<String>>` 有什么区别？**

Multimap 封装了键到集合的映射，提供了更友好的 API：
- `put()` 直接添加元素，无需手动创建 List
- `get()` 返回空集合而非 null，避免 NPE
- `size()` 返回所有元素总数，而非键的数量
- 提供了 `keys()`, `entries()`, `asMap()` 等便捷视图

**Q4: Guava EventBus 的实现原理是什么？**

EventBus 基于观察者模式，内部维护一个 `Map<Class<?>, Set<Subscriber>>` 映射：
1. `register()` 注册订阅者时，通过反射扫描 `@Subscribe` 注解的方法，将方法参数类型与订阅者关联
2. `post()` 发布事件时，根据事件类型查找匹配的订阅者列表
3. 支持事件继承：发布子类事件时，父类事件的处理方法也会被触发
4. AsyncEventBus 使用线程池异步分发事件

**Q5: Preconditions 和 Objects.requireNonNull 有什么区别？**

通常 `Objects.requireNonNull()` 抛出 NullPointerException，而 `Preconditions.checkNotNull()` 可以抛出更具体的异常类型：

```java
// Preconditions 支持自定义异常消息模板
Preconditions.checkArgument(age > 0, "年龄必须大于0，当前值: %s", age); // 抛出 IllegalArgumentException
Preconditions.checkState(!closed, "连接已关闭");                        // 抛出 IllegalStateException
Preconditions.checkNotNull(data, "数据不能为空");                        // 抛出 NullPointerException
Preconditions.checkElementIndex(3, list.size());                       // 抛出 IndexOutOfBoundsException
```

---

## 四、Apache Commons 系列

### 4.1 Commons Lang3

#### 4.1.1 工具简介

Apache Commons Lang3 是 JDK `java.lang` 包的补充，提供了大量实用的工具类，包括字符串处理、反射、对象操作、随机数生成等。

**Maven 依赖：**

```xml
<dependency>
    <groupId>org.apache.commons</groupId>
    <artifactId>commons-lang3</artifactId>
    <version>3.17.0</version>
</dependency>
```

#### 4.1.2 核心功能说明

| 工具类 | 核心方法 | 说明 |
|--------|---------|------|
| StringUtils | isEmpty, isBlank, join, split, substringBefore/After | 字符串空值安全操作 |
| ObjectUtils | defaultIfNull, firstNonNull, isNotEmpty | 对象空值处理 |
| RandomStringUtils | randomAlphanumeric, randomNumeric | 随机字符串生成 |
| RandomUtils | nextInt, nextLong, nextBoolean | 随机数生成 |
| DateUtils | addDays, truncate, parseDate | 日期操作 |
| ReflectUtils | getAllFields, getAllMethods | 反射工具 |
| Validate | notNull, isTrue, validState | 参数校验 |

#### 4.1.3 基础使用示例

```java
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.ObjectUtils;
import org.apache.commons.lang3.RandomStringUtils;

public class Lang3Demo {
    public static void main(String[] args) {
        // === StringUtils 空值安全操作 ===
        // isBlank 判断 null、空字符串、纯空格
        System.out.println(StringUtils.isBlank(null));   // true
        System.out.println(StringUtils.isBlank("  "));   // true
        System.out.println(StringUtils.isBlank("abc"));  // false

        // isEmpty 判断 null 或空字符串（不含空格）
        System.out.println(StringUtils.isEmpty("  "));   // false

        // 默认值处理
        String name = null;
        String safeName = StringUtils.defaultIfBlank(name, "匿名用户");
        System.out.println(safeName); // 输出: 匿名用户

        // 字符串截取
        String filePath = "/home/user/document.txt";
        System.out.println(StringUtils.substringAfterLast(filePath, ".")); // 输出: txt
        System.out.println(StringUtils.substringBeforeLast(filePath, "/")); // 输出: /home/user

        // === ObjectUtils 空值安全 ===
        String value = null;
        String result = ObjectUtils.defaultIfNull(value, "默认值");
        System.out.println(result); // 输出: 默认值

        // === 随机字符串生成 ===
        // 生成 6 位数字验证码
        String code = RandomStringUtils.randomNumeric(6);
        System.out.println("验证码: " + code);

        // 生成 12 位数字+字母随机字符串
        String token = RandomStringUtils.randomAlphanumeric(12);
        System.out.println("Token: " + token);
    }
}
```

### 4.2 Commons Collections4

#### 4.2.1 工具简介

Commons Collections4 扩展了 JDK 集合框架，提供了 Bag、BidiMap、LRUMap、Trie 等增强集合类型和集合工具方法。

**Maven 依赖：**

```xml
<dependency>
    <groupId>org.apache.commons</groupId>
    <artifactId>commons-collections4</artifactId>
    <version>4.4</version>
</dependency>
```

#### 4.2.2 核心使用示例

```java
import org.apache.commons.collections4.*;
import org.apache.commons.collections4.bag.HashBag;
import org.apache.commons.collections4.bidimap.DualHashBidiMap;
import org.apache.commons.collections4.map.LRUMap;
import org.apache.commons.collections4.trie.PatriciaTrie;

public class CollectionsDemo {
    public static void main(String[] args) {
        // === Bag：统计元素出现次数 ===
        Bag<String> bag = new HashBag<>();
        bag.add("苹果", 3);
        bag.add("香蕉", 2);
        bag.add("苹果", 1);
        System.out.println("苹果出现次数: " + bag.getCount("苹果")); // 输出: 4

        // === BidiMap：双向 Map，键值可互换查找 ===
        BidiMap<String, String> bidiMap = new DualHashBidiMap<>();
        bidiMap.put("中国", "CN");
        bidiMap.put("美国", "US");
        System.out.println(bidiMap.get("中国"));       // 输出: CN
        System.out.println(bidiMap.getKey("CN"));      // 输出: 中国（反向查找）

        // === LRUMap：LRU 淘汰策略的 Map ===
        LRUMap<String, String> lruMap = new LRUMap<>(3); // 最多保留 3 个
        lruMap.put("a", "1");
        lruMap.put("b", "2");
        lruMap.put("c", "3");
        lruMap.get("a");               // 访问 a，a 变为最新
        lruMap.put("d", "4");          // 淘汰最久未访问的 b
        System.out.println(lruMap.keySet()); // 输出: [c, a, d]

        // === Trie：前缀树 ===
        PatriciaTrie<String> trie = new PatriciaTrie<>();
        trie.put("apple", "苹果");
        trie.put("application", "应用程序");
        trie.put("app", "应用");
        // 按前缀查找
        System.out.println(trie.prefixMap("app")); // 输出: {app=应用, apple=苹果, application=应用程序}
    }
}
```

### 4.3 Commons IO

#### 4.3.1 工具简介

Commons IO 提供了文件操作、流操作、文件监控等实用工具，简化了 Java IO 编程。

**Maven 依赖：**

```xml
<dependency>
    <groupId>commons-io</groupId>
    <artifactId>commons-io</artifactId>
    <version>2.18.0</version>
</dependency>
```

#### 4.3.2 核心使用示例

```java
import org.apache.commons.io.FileUtils;
import org.apache.commons.io.FilenameUtils;
import org.apache.commons.io.IOUtils;
import org.apache.commons.io.filefilter.*;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;

public class IODemo {
    public static void main(String[] args) throws IOException {
        Path source = Paths.get("source.txt");
        Path target = Paths.get("target.txt");

        // === 快速读取/写入文件 ===
        String content = FileUtils.readFileToString(source.toFile(), StandardCharsets.UTF_8);
        FileUtils.writeStringToFile(target.toFile(), content, StandardCharsets.UTF_8);

        // === 复制文件/目录 ===
        FileUtils.copyFile(source.toFile(), target.toFile());
        FileUtils.copyDirectory(new File("srcDir"), new File("destDir"));

        // === 文件大小可读化 ===
        long fileSize = 1024 * 1024 * 5; // 5MB
        System.out.println(FileUtils.byteCountToDisplaySize(fileSize)); // 输出: 5 MB

        // === 文件名工具 ===
        String path = "/home/user/docs/report.pdf";
        System.out.println(FilenameUtils.getName(path));       // 输出: report.pdf
        System.out.println(FilenameUtils.getBaseName(path));   // 输出: report
        System.out.println(FilenameUtils.getExtension(path));  // 输出: pdf

        // === 流操作 ===
        try (InputStream in = new FileInputStream("input.txt");
             OutputStream out = new FileOutputStream("output.txt")) {
            // 流拷贝，自动关闭
            IOUtils.copy(in, out);
        }

        // === 文件监控 ===
        FileAlterationMonitor monitor = new FileAlterationMonitor(5000); // 5 秒扫描一次
        FileAlterationObserver observer = new FileAlterationObserver("watchDir");
        observer.addListener(new FileAlterationListenerAdaptor() {
            @Override
            public void onFileCreate(File file) {
                System.out.println("文件创建: " + file.getName());
            }
            @Override
            public void onFileDelete(File file) {
                System.out.println("文件删除: " + file.getName());
            }
        });
        monitor.addObserver(observer);
        monitor.start();
    }
}
```

### 4.4 Apache Commons 面试题

**Q1: StringUtils.isEmpty() 和 StringUtils.isBlank() 的区别？**

| 方法 | null | "" | "  " | "abc" |
|------|------|-----|------|------|
| isEmpty() | true | true | false | false |
| isBlank() | true | true | true | false |

`isBlank()` 会将纯空格字符串也视为"空"，更符合实际业务场景中的"空白输入"判断。

**Q2: Commons IO 中 FileUtils 和 JDK Files 类如何选择？**

- **JDK 7+ Files：** 推荐使用，是 JDK 原生 API，基于 NIO，性能更好，无需额外依赖
- **Commons IO FileUtils：** 提供更丰富的工具方法，如 `byteCountToDisplaySize()`、文件大小比较、目录递归操作等

实际项目中可两者配合使用，JDK 能做的优先用 JDK。

**Q3: Bag 和 Map 在统计次数时有什么区别？**

使用 Map 统计元素次数需要手动判空和累加：

```java
// Map 方式：代码繁琐
Map<String, Integer> map = new HashMap<>();
map.put("苹果", map.getOrDefault("苹果", 0) + 1);

// Bag 方式：一行搞定
Bag<String> bag = new HashBag<>();
bag.add("苹果");
```

Bag 内部封装了计数逻辑，代码更简洁，语义更清晰。

**Q4: LRUMap 的实现原理？**

LRUMap 基于 LinkedHashMap 的扩展实现，继承自 `AbstractHashedMap`，内部使用双向链表维护访问顺序。当 map 容量超过设定阈值时，自动删除链表头部（最久未访问）的元素。核心机制：
1. `get()` 操作会将访问的元素移到链表尾部
2. `put()` 操作时检查 size，超过最大容量调用 `removeLRU()` 删除链表头部元素

---

## 五、Jackson —— JSON 处理

### 5.1 工具简介

Jackson 是 Java 生态中最流行的 JSON 处理库，Spring Boot 默认集成。提供了高性能的 JSON 序列化/反序列化、树模型、数据绑定等功能。

**核心模块：**

| 模块 | 功能 |
|------|------|
| jackson-databind | 数据绑定（核心） |
| jackson-core | 底层流式 API |
| jackson-annotations | 注解支持 |
| jackson-datatype-jsr310 | Java 8 时间类型支持 |
| jackson-datatype-jdk8 | Optional 等 JDK 8 类型支持 |

**Maven 依赖：**

```xml
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
    <version>2.18.2</version>
</dependency>
<dependency>
    <groupId>com.fasterxml.jackson.datatype</groupId>
    <artifactId>jackson-datatype-jsr310</artifactId>
    <version>2.18.2</version>
</dependency>
```

### 5.2 核心功能说明

| 功能 | 说明 |
|------|------|
| 序列化 | Java 对象 → JSON 字符串 |
| 反序列化 | JSON 字符串 → Java 对象 |
| 注解控制 | @JsonProperty, @JsonIgnore, @JsonFormat 等 |
| 树模型 | JsonNode 方式读写 JSON |
| 流式 API | JsonParser / JsonGenerator 高性能读写 |
| 多态反序列化 | @JsonTypeInfo / @JsonSubTypes |
| 自定义序列化器 | JsonSerializer / JsonDeserializer |

### 5.3 基础使用示例

```java
import com.fasterxml.jackson.annotation.*;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.*;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import java.time.LocalDateTime;
import java.util.*;

// 实体类定义
@Data
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL) // 序列化时忽略 null 字段
public class Article {
    @JsonProperty("article_id")    // 指定 JSON 字段名
    private Long id;

    private String title;

    @JsonIgnore                     // 序列化时忽略此字段
    private String secretKey;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss") // 日期格式化
    private LocalDateTime createTime;

    private List<String> tags;
}

public class JacksonDemo {
    public static void main(String[] args) throws Exception {
        // 配置 ObjectMapper（全局单例，线程安全）
        ObjectMapper mapper = new ObjectMapper();
        // 注册 Java 8 时间模块
        mapper.registerModule(new JavaTimeModule());
        // 禁用将日期写为时间戳
        mapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
        // 忽略未知属性
        mapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);

        // === 序列化：Java 对象 → JSON 字符串 ===
        Article article = new Article();
        article.setId(1L);
        article.setTitle("Jackson 使用指南");
        article.setSecretKey("should-be-hidden");
        article.setCreateTime(LocalDateTime.now());
        article.setTags(Arrays.asList("Java", "JSON"));

        String json = mapper.writerWithDefaultPrettyPrinter()
                .writeValueAsString(article);
        System.out.println(json);
        /* 输出:
        {
          "article_id" : 1,
          "title" : "Jackson 使用指南",
          "createTime" : "2025-01-01 12:00:00",
          "tags" : [ "Java", "JSON" ]
        }
        */

        // === 反序列化：JSON 字符串 → Java 对象 ===
        String jsonStr = "{\"article_id\":2,\"title\":\"另一篇文章\"}";
        Article parsed = mapper.readValue(jsonStr, Article.class);

        // === 泛型反序列化：List/Map ===
        String listJson = "[{\"article_id\":1,\"title\":\"A\"},{\"article_id\":2,\"title\":\"B\"}]";
        List<Article> list = mapper.readValue(listJson, 
                new TypeReference<List<Article>>() {});
    }
}
```

### 5.4 高级特性

**树模型 —— JsonNode：**

```java
// 树模型：不需要预先定义实体类即可操作 JSON
String json = "{\"name\":\"张三\",\"age\":25,\"scores\":[90,85,88]}";
JsonNode root = mapper.readTree(json);

String name = root.get("name").asText();
int age = root.get("age").asInt();
JsonNode scores = root.get("scores");
System.out.println("第一科成绩: " + scores.get(0).asInt()); // 输出: 90

// 动态构建 JSON
ObjectNode node = mapper.createObjectNode();
node.put("name", "李四");
node.put("age", 30);
ArrayNode arr = node.putArray("hobbies");
arr.add("篮球");
arr.add("编程");
```

**多态反序列化：**

```java
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "type")
@JsonSubTypes({
    @JsonSubTypes.Type(value = Dog.class, name = "dog"),
    @JsonSubTypes.Type(value = Cat.class, name = "cat")
})
public abstract class Animal {
    private String name;
}

public class Dog extends Animal {
    private String breed;
}

public class Cat extends Animal {
    private String color;
}

// 反序列化时根据 type 字段自动选择子类
String json = "{\"type\":\"dog\",\"name\":\"旺财\",\"breed\":\"金毛\"}";
Animal animal = mapper.readValue(json, Animal.class); // 实际类型为 Dog
```

**自定义序列化器：**

```java
// 自定义序列化器：金额单位从分转为元
public class MoneySerializer extends JsonSerializer<Long> {
    @Override
    public void serialize(Long value, JsonGenerator gen, 
                          SerializerProvider serializers) throws IOException {
        // 分转元，保留两位小数
        gen.writeNumber(new BigDecimal(value).divide(new BigDecimal(100)));
    }
}

// 使用
@Data
public class Order {
    @JsonSerialize(using = MoneySerializer.class)
    private Long amount; // 单位：分
}
```

### 5.5 注意事项

1. **ObjectMapper 是线程安全的：** 全局使用单例，避免重复创建（创建成本高）。
2. **日期处理：** 务必注册 `JavaTimeModule`，否则 `LocalDateTime` 等类型无法正常序列化。
3. **循环引用：** 双向关联的对象会触发无限递归，使用 `@JsonManagedReference` / `@JsonBackReference` 或 `@JsonIgnore` 解决。
4. **大 JSON 解析：** 超大 JSON 文件使用流式 API（JsonParser）而非一次性读取，避免 OOM。
5. **反序列化安全：** 不要反序列化不可信来源的 JSON 到 `Object.class`，可能触发反序列化漏洞。

### 5.6 常见问题解答

**Q1: Jackson 和 Fastjson、Gson 如何选择？**
Jackson 性能最佳、生态最完善、Spring Boot 默认集成，是首选。Gson 轻量简洁，适合简单场景。Fastjson 安全性问题较多，不再推荐。

**Q2: @JsonIgnore 和 @JsonIgnoreProperties 的区别？**
@JsonIgnore 用于单个字段，@JsonIgnoreProperties 用于类级别忽略一组字段，支持忽略未知属性。

### 5.7 面试题

**Q1: Jackson 序列化时如何忽略 null 值？**

三种方式：

```java
// 1. 类级别注解
@JsonInclude(JsonInclude.Include.NON_NULL)
public class User { ... }

// 2. ObjectMapper 全局配置
mapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);

// 3. 字段级别注解
@JsonInclude(JsonInclude.Include.NON_NULL)
private String nickName;
```

**Q2: Jackson 如何处理 JSON 中包含未知属性？**

默认情况下 Jackson 遇到未知属性会抛出 `UnrecognizedPropertyException`。解决方案：

```java
// 方式1：全局配置
mapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);

// 方式2：类级别注解
@JsonIgnoreProperties(ignoreUnknown = true)
public class User { ... }
```

**Q3: Jackson 的序列化原理是什么？**

Jackson 序列化流程：
1. **查找序列化器：** 根据目标类型从 `SerializerProvider` 中查找对应的 `JsonSerializer`
2. **BeanSerializer：** 对 POJO 类型，使用 `BeanSerializer`，通过反射获取所有 getter 方法
3. **字段过滤：** 根据注解（@JsonIgnore, @JsonInclude 等）过滤字段
4. **流式输出：** 通过 `JsonGenerator` 将字段逐个写入 JSON 流

**Q4: 如何实现 JSON 字段的局部更新（PATCH）？**

```java
// 使用 @JsonMerge 注解实现局部更新
@Data
public class UserDTO {
    private String name;

    @JsonMerge
    private List<String> tags; // 合并而非覆盖
}

// 或使用 ObjectMapper 的 updateValue 方法
User existing = getUserFromDB();
mapper.readerForUpdating(existing).readValue(patchJson);
```

**Q5: Jackson 的 TypeReference 解决了什么问题？**

Java 泛型在运行时会被擦除，`List<Article>.class` 这种写法是不合法的。`TypeReference` 通过匿名内部类保留泛型信息：

```java
// 错误：运行时无法获取泛型类型
List<Article> list = mapper.readValue(json, List.class); // 得到 List<Map>

// 正确：TypeReference 保留泛型信息
List<Article> list = mapper.readValue(json, new TypeReference<List<Article>>() {});
```

**Q6: 如何提高 Jackson 大数据量序列化的性能？**

1. **使用流式 API：** 不依赖反射，直接操作 `JsonGenerator`/`JsonParser`
2. **使用 Afterburner 模块：** 字节码增强代替反射
3. **复用 ObjectMapper：** 全局单例，避免重复创建
4. **关闭不必要的功能：** 如 `FAIL_ON_UNKNOWN_PROPERTIES`
5. **使用 `writeValue` 直接写流：** 避免中间字符串产生

---

## 六、Mockito —— 单元测试 Mock 框架

### 6.1 工具简介

Mockito 是 Java 最流行的 Mock 框架，用于单元测试中模拟依赖对象的行为，使测试专注于被测代码逻辑，隔离外部依赖。

**Maven 依赖：**

```xml
<dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-core</artifactId>
    <version>5.14.2</version>
    <scope>test</scope>
</dependency>
<!-- 与 JUnit 5 集成 -->
<dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-junit-jupiter</artifactId>
    <version>5.14.2</version>
    <scope>test</scope>
</dependency>
```

### 6.2 核心功能说明

| 功能 | 说明 |
|------|------|
| 创建 Mock 对象 | `mock()`, `@Mock`, `@MockBean` |
| 方法打桩 | `when().thenReturn()`, `when().thenThrow()` |
| 行为验证 | `verify()`, `times()`, `never()`, `atLeastOnce()` |
| 参数匹配 | `any()`, `eq()`, `argThat()`, `ArgumentCaptor` |
| 部分 Mock | `@Spy`, `spy()` |
| 静态方法 Mock | `mockStatic()` (Mockito 3.4+) |
| BDD 风格 | `given().willReturn()` / `then().should()` |

### 6.3 基础使用示例

```java
// 假设的业务代码
@Service
public class UserService {
    @Autowired
    private UserRepository userRepository;
    @Autowired
    private EmailService emailService;

    public User createUser(String name, String email) {
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("用户名不能为空");
        }
        User user = new User(name, email);
        User saved = userRepository.save(user);
        emailService.sendWelcomeEmail(email);
        return saved;
    }
}

// 测试代码
@ExtendWith(MockitoExtension.class) // JUnit 5 集成
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private EmailService emailService;

    @InjectMocks // 自动将 @Mock 注入到被测试对象
    private UserService userService;

    @Test
    @DisplayName("正常创建用户")
    void testCreateUserSuccess() {
        // Given: 准备测试数据和行为
        User expectedUser = new User("张三", "zhangsan@test.com");
        when(userRepository.save(any(User.class))).thenReturn(expectedUser);

        // When: 执行被测方法
        User result = userService.createUser("张三", "zhangsan@test.com");

        // Then: 验证结果
        assertEquals("张三", result.getName());
        // 验证 emailService.sendWelcomeEmail() 被调用了一次
        verify(emailService, times(1)).sendWelcomeEmail("zhangsan@test.com");
    }

    @Test
    @DisplayName("用户名为空时抛出异常")
    void testCreateUserWithEmptyName() {
        // 验证抛出指定异常
        assertThrows(IllegalArgumentException.class, () -> {
            userService.createUser("", "test@test.com");
        });
        // 验证 repository 没有被调用
        verify(userRepository, never()).save(any());
    }
}
```

### 6.4 高级特性

**参数捕获器（ArgumentCaptor）：**

```java
@Test
void testArgumentCaptor() {
    userService.createUser("张三", "zhangsan@test.com");

    // 捕获传给 save 方法的参数
    ArgumentCaptor<User> captor = ArgumentCaptor.forClass(User.class);
    verify(userRepository).save(captor.capture());

    User capturedUser = captor.getValue();
    assertEquals("张三", capturedUser.getName());
}
```

**@Spy 部分 Mock：**

```java
@Test
void testSpy() {
    // Spy 会调用真实方法，但可以 Mock 特定方法
    List<String> spyList = spy(new ArrayList<>());

    // Mock size() 方法，其他方法走真实逻辑
    when(spyList.size()).thenReturn(100);

    spyList.add("element1"); // 真实调用 add()
    System.out.println(spyList.size()); // 输出: 100（Mock 的返回值）
    System.out.println(spyList.get(0));  // 输出: element1（真实调用 get()）
}
```

**静态方法 Mock：**

```java
@Test
void testStaticMock() {
    try (MockedStatic<UUID> mockedUUID = mockStatic(UUID.class)) {
        String fixedUuid = "12345678-1234-1234-1234-123456789abc";
        mockedUUID.when(UUID::randomUUID).thenReturn(UUID.fromString(fixedUuid));

        String result = UUID.randomUUID().toString();
        assertEquals(fixedUuid, result);
    } // try-with-resources 自动关闭静态 Mock
}
```

**BDD 风格（更符合行为驱动开发）：**

```java
@Test
@DisplayName("BDD风格测试")
void testBDDStyle() {
    // Given
    User expectedUser = new User("张三", "zhangsan@test.com");
    given(userRepository.save(any(User.class))).willReturn(expectedUser);

    // When
    User result = userService.createUser("张三", "zhangsan@test.com");

    // Then
    then(emailService).should(times(1)).sendWelcomeEmail("zhangsan@test.com");
}
```

### 6.5 注意事项

1. **不能 Mock final 类：** 默认 Mockito 不能 mock final 类，需在 `src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker` 中配置 `mock-maker-inline`。
2. **不要滥用 Mock：** 只 Mock 外部依赖，不要 Mock 值对象、POJO、DTO。
3. **@Mock 和 @MockBean 的区别：** @Mock 是纯 Mockito 注解，@MockBean 是 Spring Boot Test 提供的，会将 Mock 对象注入 Spring 容器。
4. **静态方法 Mock 需及时关闭：** 使用 try-with-resources 确保静态 Mock 的线程安全性。
5. **避免 Mock 过多：** 如果测试中 Mock 超过 3-4 个，说明待测类可能职责过重，需要重构。

### 6.6 常见问题解答

**Q1: @InjectMocks 和手动创建有什么区别？**
@InjectMocks 会自动通过构造器注入、Setter 注入或字段注入将 @Mock 和 @Spy 对象注入到被测试对象中，减少了手动创建和赋值的样板代码。

**Q2: 如何 Mock void 方法？**
使用 `doNothing()`、`doThrow()` 或 `doAnswer()`：

```java
doNothing().when(mockService).deleteById(anyLong());
doThrow(new RuntimeException()).when(mockService).deleteById(1L);
```

### 6.7 面试题

**Q1: Mock 和 Stub 的区别是什么？**

| 概念 | 说明 | Mockito 示例 |
|------|------|-------------|
| Stub（打桩） | 为方法调用提供预定义返回值，不关心调用情况 | `when(x.get()).thenReturn(y)` |
| Mock（模拟） | 不仅提供返回值，还能验证方法是否被调用、调用次数等 | `verify(x).get()` |

Mockito 中 `when().thenReturn()` 是打桩，`verify()` 是验证行为，两者结合使用。

**Q2: @Mock 和 @Spy 的区别？**

| 对比维度 | @Mock | @Spy |
|---------|-------|------|
| 默认行为 | 所有方法调用返回默认值（null/0/false） | 执行真实方法 |
| 打桩方式 | `when().thenReturn()` | `doReturn().when()` 避免调用真实方法 |
| 使用场景 | 完全隔离依赖 | 部分 Mock，保留部分真实逻辑 |
| 创建方式 | `mock(Class)` | `spy(new Object())` |

**Q3: Mockito 如何实现对静态方法的 Mock？**

Mockito 3.4+ 通过 `Mockito.mockStatic()` 实现，底层使用 `Instrumentation` 和 `ByteBuddy` 在运行时修改类的字节码，将对静态方法的调用重定向到 Mock 逻辑。使用时需注意：
1. 必须在 try-with-resources 中创建，确保测试结束后恢复
2. 同时只能 Mock 一个静态类，嵌套使用需注意
3. 可能影响测试性能，不建议大量使用

**Q4: `doReturn().when()` 和 `when().thenReturn()` 有什么区别？**

```java
// when().thenReturn() 会实际调用方法（对 Spy 对象有风险）
when(spy.get(0)).thenReturn("first"); // 会真实调用 spy.get(0)！

// doReturn().when() 不会调用真实方法，更安全
doReturn("first").when(spy).get(0);   // 不调用真实方法
```

对 @Mock 对象两者效果相同，但对 @Spy 对象必须使用 `doReturn()` 方式，否则真实方法会被调用。

**Q5: 如何测试一个依赖了外部 API 的 Service 方法？**

```java
@Test
void testServiceWithExternalAPI() {
    // 1. Mock 外部 API 调用
    when(externalApiClient.getUserInfo(anyString()))
            .thenReturn(new UserInfo("张三", 25));

    // 2. Mock 异常场景
    when(externalApiClient.getUserInfo("error"))
            .thenThrow(new TimeoutException("API 调用超时"));

    // 3. 验证重试逻辑
    when(externalApiClient.getUserInfo("retry"))
            .thenThrow(new TimeoutException("首次失败"))
            .thenReturn(new UserInfo("李四", 30)); // 第二次成功

    // 4. 验证结果
    UserInfo result = retryService.getUserInfo("retry");
    assertEquals("李四", result.getName());
    verify(externalApiClient, times(2)).getUserInfo("retry");
}
```

**Q6: Mockito 的 verify 方法有哪些常用模式？**

```java
// 验证调用次数
verify(mock).method();               // 默认验证调用 1 次
verify(mock, times(2)).method();     // 精确调用 2 次
verify(mock, atLeastOnce()).method(); // 至少 1 次
verify(mock, atLeast(3)).method();   // 至少 3 次
verify(mock, atMost(5)).method();    // 最多 5 次
verify(mock, never()).method();      // 从未调用

// 验证调用顺序
InOrder inOrder = inOrder(mock1, mock2);
inOrder.verify(mock1).firstMethod();
inOrder.verify(mock2).secondMethod();

// 验证超时（异步场景）
verify(mock, timeout(1000)).asyncMethod();       // 1 秒内被调用
verify(mock, timeout(1000).times(2)).asyncMethod(); // 1 秒内被调用 2 次

// 验证后不再有交互
verifyNoMoreInteractions(mock);
```

---

## 七、Hutool —— 国产 Java 工具集

### 7.1 工具简介

Hutool 是国内使用最广泛的 Java 工具集，涵盖了文件、日期、加密、网络、HTTP、图片、Excel 等几乎所有日常开发场景，提供"一个工具类，一个方法"的便捷体验。

**Maven 依赖：**

```xml
<dependency>
    <groupId>cn.hutool</groupId>
    <artifactId>hutool-all</artifactId>
    <version>5.8.34</version>
</dependency>
```

### 7.2 核心功能说明

| 模块 | 核心类 | 说明 |
|------|--------|------|
| 类型转换 | Convert | 任意类型转换，如 `Convert.toInt(str)` |
| 日期时间 | DateUtil | 日期格式化、计算、比较 |
| 字符串 | StrUtil | 字符串工具（类似 StringUtils） |
| 集合 | CollUtil | 集合操作、创建、过滤 |
| 文件 | FileUtil | 文件读写、复制、删除 |
| HTTP | HttpUtil | HTTP 请求客户端 |
| JSON | JSONUtil | JSON 解析（基于 Jackson） |
| 加密 | SecureUtil | MD5、SHA、AES、RSA 等 |
| 图片 | ImgUtil | 图片缩放、裁剪、水印 |
| Excel | ExcelUtil | Excel 读写（基于 POI） |
| 验证码 | CaptchaUtil | 图形验证码生成 |
| 定时任务 | CronUtil | 轻量级定时任务 |

### 7.3 基础使用示例

```java
import cn.hutool.core.convert.Convert;
import cn.hutool.core.date.DateUtil;
import cn.hutool.core.util.StrUtil;
import cn.hutool.crypto.SecureUtil;
import cn.hutool.http.HttpUtil;
import cn.hutool.json.JSONUtil;

public class HutoolDemo {
    public static void main(String[] args) {
        // === 类型转换 ===
        int num = Convert.toInt("123", 0);         // 转换失败返回默认值 0
        String dateStr = Convert.toStr(LocalDate.now());

        // === 日期工具 ===
        String now = DateUtil.now();               // 2025-01-01 12:00:00
        String today = DateUtil.today();           // 2025-01-01
        // 计算两个日期相差天数
        long between = DateUtil.between(
                DateUtil.parse("2025-01-01"),
                DateUtil.parse("2025-01-15"),
                DateUnit.DAY
        );

        // === 字符串工具 ===
        String template = "你好，{}！你的订单{}已发货。";
        String msg = StrUtil.format(template, "张三", "ORD12345");
        // 输出: 你好，张三！你的订单ORD12345已发货。

        // === HTTP 请求 ===
        String result = HttpUtil.get("https://api.example.com/data");
        // POST 请求
        String postResult = HttpUtil.post("https://api.example.com/submit", 
                "{\"name\":\"test\"}");

        // === JSON 处理 ===
        User user = new User("张三", 25);
        String json = JSONUtil.toJsonStr(user);
        User parsed = JSONUtil.toBean(json, User.class);

        // === 加密 ===
        String md5 = SecureUtil.md5("hello");
        String sha256 = SecureUtil.sha256("hello");
    }
}
```

### 7.4 高级特性

**Excel 读写：**

```java
// 读取 Excel
List<User> users = ExcelUtil.getReader("users.xlsx")
        .addHeaderAlias("用户名", "name")   // 表头别名
        .addHeaderAlias("年龄", "age")
        .readAll(User.class);

// 写入 Excel
ExcelUtil.getWriter("output.xlsx")
        .write(users, true)  // true 表示写入表头
        .flush();
```

**验证码生成：**

```java
// 生成线段干扰的验证码并输出到文件
CaptchaUtil.createLineCaptcha(200, 100, 4, 20)
        .write("captcha.png");
```

**轻量定时任务：**

```java
// 配置文件 cron.setting
// [demo]
// cron.job = com.example.DemoJob
// cron.cron = 0 */5 * * * *

// 启动定时任务
CronUtil.start();
```

### 7.5 注意事项

1. **按需引入：** 生产环境建议使用 `hutool-bom` 按模块引入，避免引入无用的 `hutool-all`。
2. **JSONUtil 底层依赖：** 默认使用 Jackson，需确保 classpath 中有 Jackson 依赖。
3. **Excel 大数据量：** 对于超大 Excel 文件，建议使用 `ExcelUtil.getReader()` 的流式读取模式。
4. **线程安全：** 大部分工具类方法是线程安全的，无需额外处理。

### 7.6 面试题

**Q1: Hutool 和 Guava、Apache Commons 相比有什么优势？**

1. **功能更全面：** Hutool 涵盖了 Commons 和 Guava 的大部分功能，还额外提供了 HTTP、Excel、加密、二维码等模块
2. **更适合中国开发者：** 中文文档完善，API 设计更符合国内开发习惯
3. **一站式方案：** 一个依赖即可满足日常开发 80% 以上的工具需求
4. **轻量级：** 各模块独立，可按需引入

**Q2: Hutool 的 Convert 类是如何实现类型转换的？**

Convert 类内部维护了一个 `ConverterRegistry`（转换器注册表），通过目标类型查找对应的 `Converter` 实现。核心流程：
1. 根据目标类型查找注册的 Converter
2. 如果未找到，尝试查找通用的 Converter（如 `NumberConverter`）
3. 如果转换失败，可返回指定的默认值，避免异常

**Q3: 使用 Hutool 的 HttpUtil 和 RestTemplate 有什么不同？**

| 对比维度 | Hutool HttpUtil | Spring RestTemplate |
|---------|----------------|---------------------|
| 依赖 | 无需 Spring | 需要 Spring 环境 |
| API 风格 | 链式调用，简洁 | 模板方法，功能丰富 |
| 连接池 | 简单支持 | 可配置连接池 |
| 使用场景 | 简单 HTTP 调用、工具类 | Spring 微服务间调用 |

---

## 八、JUnit 5 —— 测试框架

### 8.1 工具简介

JUnit 5 是 Java 单元测试框架的最新版本，由 JUnit Platform（测试引擎）、JUnit Jupiter（新编程模型）和 JUnit Vintage（兼容 JUnit 3/4）三部分组成。Spring Boot 2.2+ 默认使用 JUnit 5。

**Maven 依赖：**

```xml
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.11.4</version>
    <scope>test</scope>
</dependency>
```

### 8.2 核心功能说明

| 注解 | 说明 |
|------|------|
| `@Test` | 标记测试方法 |
| `@BeforeEach` / `@AfterEach` | 每个测试方法前后执行 |
| `@BeforeAll` / `@AfterAll` | 所有测试方法前后执行（静态方法） |
| `@DisplayName` | 测试方法显示名称 |
| `@Disabled` | 禁用测试方法 |
| `@ParameterizedTest` | 参数化测试 |
| `@RepeatedTest` | 重复测试 |
| `@TestMethodOrder` | 指定测试执行顺序 |
| `@Tag` | 测试分类标签 |

### 8.3 基础使用示例

```java
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.*;

import java.util.stream.Stream;

@DisplayName("用户服务测试")
class UserServiceJUnit5Test {

    private UserService userService;

    @BeforeAll
    static void initAll() {
        System.out.println("=== 开始测试（只执行一次）===");
    }

    @BeforeEach
    void init() {
        // 每个测试方法执行前初始化
        userService = new UserService();
    }

    @Test
    @DisplayName("正常创建用户")
    void testCreateUser() {
        User user = userService.createUser("张三", "zhangsan@test.com");
        assertNotNull(user);
        assertEquals("张三", user.getName());
        // 分组断言
        assertAll("用户信息",
                () -> assertEquals("张三", user.getName()),
                () -> assertEquals("zhangsan@test.com", user.getEmail())
        );
    }

    @Test
    @DisplayName("测试异常场景")
    void testException() {
        // 验证抛出指定异常
        IllegalArgumentException ex = assertThrows(
                IllegalArgumentException.class,
                () -> userService.createUser(null, "test@test.com")
        );
        assertTrue(ex.getMessage().contains("用户名不能为空"));
    }

    @Test
    @DisplayName("测试超时")
    void testTimeout() {
        // 验证方法在 1 秒内完成
        assertTimeout(Duration.ofSeconds(1), () -> {
            userService.createUser("张三", "test@test.com");
        });
    }

    // === 参数化测试 ===
    @ParameterizedTest
    @ValueSource(strings = {"", "  ", "\t"})
    @DisplayName("空白用户名应抛出异常")
    void testEmptyName(String name) {
        assertThrows(IllegalArgumentException.class,
                () -> userService.createUser(name, "test@test.com"));
    }

    @ParameterizedTest
    @CsvSource({
            "张三, zhangsan@test.com, true",
            "'', test@test.com, false",
            "null, test@test.com, false"
    })
    @DisplayName("批量测试用户创建")
    void testCreateUserBatch(String name, String email, boolean expected) {
        if (expected) {
            assertDoesNotThrow(() -> userService.createUser(name, email));
        }
    }
}
```

### 8.4 高级特性

**嵌套测试：**

```java
@DisplayName("订单服务测试")
class OrderServiceTest {

    @Nested
    @DisplayName("创建订单")
    class CreateOrder {
        @Test
        @DisplayName("正常创建")
        void testNormalCreate() { /* ... */ }

        @Test
        @DisplayName("库存不足")
        void testInsufficientStock() { /* ... */ }
    }

    @Nested
    @DisplayName("取消订单")
    class CancelOrder {
        @Test
        @DisplayName("正常取消")
        void testNormalCancel() { /* ... */ }

        @Test
        @DisplayName("已发货不可取消")
        void testCancelShippedOrder() { /* ... */ }
    }
}
```

**@MethodSource 方法数据源：**

```java
@ParameterizedTest
@MethodSource("provideUserData")
@DisplayName("方法源参数化测试")
void testWithMethodSource(String name, int age, boolean valid) {
    // ...
}

static Stream<Arguments> provideUserData() {
    return Stream.of(
            Arguments.of("张三", 25, true),
            Arguments.of("", 25, false),
            Arguments.of("李四", -1, false)
    );
}
```

### 8.5 注意事项

1. **@BeforeAll / @AfterAll 必须是静态方法：** 除非测试类使用 `@TestInstance(Lifecycle.PER_CLASS)`。
2. **参数化测试依赖：** 需要额外添加 `junit-jupiter-params` 依赖（junit-jupiter 聚合包已包含）。
3. **@Test 和 @RepeatedTest 不共存：** 一个方法不能同时使用两者。
4. **断言顺序：** `assertAll()` 中的断言会全部执行，不会因为前面的断言失败而跳过后续断言。

### 8.6 面试题

**Q1: JUnit 5 和 JUnit 4 的主要区别？**

| 对比维度 | JUnit 4 | JUnit 5 |
|---------|---------|---------|
| 架构 | 单一 jar | 三模块：Platform + Jupiter + Vintage |
| 包名 | `org.junit` | `org.junit.jupiter` |
| 初始化注解 | @Before / @After | @BeforeEach / @AfterEach |
| 扩展机制 | @RunWith + Runner | @ExtendWith + Extension |
| 断言库 | 内置 assert | 支持 Lambda 断言 |
| 参数化测试 | 需要 @RunWith(Parameterized.class) | @ParameterizedTest |
| 可见性 | 方法必须 public | 方法可以是 package-private |

**Q2: @BeforeEach 和 @BeforeAll 的区别？**

- `@BeforeEach`：每个 @Test 方法执行前调用，用于初始化每个测试共享的测试数据
- `@BeforeAll`：所有 @Test 方法执行前调用一次，用于初始化数据库连接等昂贵资源

**Q3: 如何实现测试用例之间的依赖和顺序？**

```java
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class OrderedTest {
    @Test
    @Order(1)
    void first() { /* 先执行 */ }

    @Test
    @Order(2)
    void second() { /* 后执行 */ }
}
```

但通常不推荐测试用例之间有依赖，每个测试应该是独立的。

**Q4: JUnit 5 的扩展机制（Extension）与 JUnit 4 的 Runner 有什么区别？**

JUnit 5 的 Extension 是一个更灵活的组合式扩展机制：
- 一个测试类可以使用多个 `@ExtendWith`，而 JUnit 4 只能使用一个 `@RunWith`
- Extension 通过回调接口（如 `BeforeEachCallback`, `AfterTestExecutionCallback`）实现，职责单一
- 支持自动注册（通过 SPI 机制），无需在每个测试类上声明

**Q5: 如何测试私有方法？**

通常不建议直接测试私有方法，应通过公有方法间接测试。如果确实需要，可以使用反射：

```java
@Test
void testPrivateMethod() throws Exception {
    MyService service = new MyService();
    Method method = MyService.class.getDeclaredMethod("privateMethod", String.class);
    method.setAccessible(true);
    String result = (String) method.invoke(service, "test");
    assertEquals("expected", result);
}
```

但更好的做法是反思设计：如果私有方法足够复杂需要单独测试，可能应该提取为独立的类。

---

## 附录：工具版本兼容性参考

| 工具 | 推荐版本 | 最低 JDK | 说明 |
|------|---------|---------|------|
| Lombok | 1.18.36 | 8 | JDK 21 需 1.18.30+ |
| SLF4J | 2.0.16 | 8 | 2.x 支持 lambda 日志 |
| Logback | 1.5.12 | 8 | SLF4J 原生实现 |
| Guava | 33.4.0-jre | 8 | jre 版本不含 Android |
| Commons Lang3 | 3.17.0 | 8 | 注意与 Lang2 不兼容 |
| Commons Collections4 | 4.4 | 8 | 与 Collections3 不兼容 |
| Commons IO | 2.18.0 | 8 | — |
| Jackson | 2.18.2 | 8 | 2.x 系列最后一个大版本 |
| Mockito | 5.14.2 | 8 | 5.x 支持 JDK 21 |
| Hutool | 5.8.34 | 8 | 最新稳定版 |
| JUnit 5 | 5.11.4 | 8 | Spring Boot 2.2+ 默认 |

---

> **文档说明：** 本文档旨在为 Java 开发者提供常用工具库的快速参考和面试准备。建议结合官方文档和实际项目使用，加深理解。代码示例均可直接编译运行，依赖版本为编写时最新稳定版。