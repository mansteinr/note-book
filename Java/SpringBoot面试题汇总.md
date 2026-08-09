# Spring Boot 面试题汇总

## 目录
- [一、Spring Boot 基础](#一spring-boot-基础)
- [二、自动配置原理](#二自动配置原理)
- [三、依赖注入与 IoC 容器](#三依赖注入与-ioc-容器)
- [四、配置管理](#四配置管理)
- [五、AOP 面向切面编程](#五aop-面向切面编程)
- [六、数据访问与事务管理](#六数据访问与事务管理)
- [七、RESTful API 设计](#七restful-api-设计)
- [八、安全认证与授权](#八安全认证与授权)
- [九、异常处理与统一响应](#九异常处理与统一响应)
- [十、微服务与集成](#十微服务与集成)
- [十一、测试](#十一测试)
- [十二、性能优化与监控](#十二性能优化与监控)
- [十三、综合实战](#十三综合实战)

---

## 一、Spring Boot 基础

**Q1：什么是 Spring Boot？它的核心特性是什么？**

**答：**
Spring Boot 是 Spring 框架的一个子项目，旨在简化 Spring 应用的初始搭建和开发过程。它通过"约定优于配置"的理念，提供了开箱即用的体验。

**核心特性：**

| 特性 | 说明 |
|-----|------|
| 自动配置 | 根据类路径中的依赖自动配置 Spring 应用 |
| 起步依赖（Starter） | 一站式引入所需依赖，解决版本冲突 |
| 内嵌服务器 | 内置 Tomcat、Jetty、Undertow，无需部署 WAR |
| Actuator | 生产级监控端点，健康检查、指标收集 |
| 外部化配置 | 支持 properties、YAML、环境变量、命令行参数 |
| 无代码生成 | 无需 XML 配置，无需代码生成 |

```java
// Spring Boot 应用入口
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

---

**Q2：`@SpringBootApplication` 注解包含哪些注解？**

**答：**
`@SpringBootApplication` 是一个组合注解，包含三个核心注解：

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Inherited
@SpringBootConfiguration  // 标识为 Spring Boot 配置类
@EnableAutoConfiguration  // 启用自动配置
@ComponentScan(excludeFilters = {  // 组件扫描
    @Filter(type = FilterType.CUSTOM, classes = TypeExcludeFilter.class),
    @Filter(type = FilterType.CUSTOM, classes = AutoConfigurationExcludeFilter.class)
})
public @interface SpringBootApplication {
    // ...
}
```

| 注解 | 作用 |
|-----|------|
| `@SpringBootConfiguration` | 标记为配置类，继承自 `@Configuration` |
| `@EnableAutoConfiguration` | 启用 Spring Boot 自动配置机制 |
| `@ComponentScan` | 扫描当前包及子包中的组件（@Component、@Service、@Controller 等） |

---

**Q3：Spring Boot 的启动流程是怎样的？**

**答：**
Spring Boot 启动流程主要分为以下阶段：

```text
1. 创建 SpringApplication 实例
   ├── 推断应用类型（Servlet/Reactive/None）
   ├── 加载 ApplicationContextInitializer
   └── 加载 ApplicationListener

2. 执行 SpringApplication.run()
   ├── 获取并启动 SpringApplicationRunListener
   ├── 准备环境（Environment）
   │   ├── 加载配置文件
   │   └── 绑定命令行参数
   ├── 创建 ApplicationContext
   ├── 准备 ApplicationContext
   │   ├── 执行 Initializer
   │   ├── 加载 Bean 定义
   │   └── 执行 BeanFactoryPostProcessor
   ├── 刷新 ApplicationContext
   │   ├── 实例化单例 Bean
   │   ├── 执行自动配置
   │   └── 启动内嵌 Web 服务器
   └── 执行 ApplicationRunner 和 CommandLineRunner
```

**核心代码：**
```java
public ConfigurableApplicationContext run(String... args) {
    // 1. 创建并启动计时器
    StopWatch stopWatch = new StopWatch();
    stopWatch.start();
    
    // 2. 准备环境
    ConfigurableApplicationContext context = null;
    ConfigurableEnvironment environment = prepareEnvironment(listeners, applicationArguments);
    
    // 3. 创建 ApplicationContext
    context = createApplicationContext();
    
    // 4. 准备上下文
    prepareContext(context, environment, listeners, applicationArguments, printedBanner);
    
    // 5. 刷新上下文（核心：加载 Bean、自动配置）
    refreshContext(context);
    
    // 6. 后置处理
    afterRefresh(context, applicationArguments);
    
    stopWatch.stop();
    return context;
}
```

---

**Q4：Spring Boot 的 Starter 是什么？如何自定义 Starter？**

**答：**
Starter 是一组依赖描述符，可以一站式引入所需的技术栈。

**常用 Starter：**
| Starter | 说明 |
|---------|------|
| `spring-boot-starter-web` | Web 应用（含 Tomcat + Spring MVC） |
| `spring-boot-starter-data-jpa` | JPA + Hibernate |
| `spring-boot-starter-data-redis` | Redis |
| `spring-boot-starter-security` | Spring Security |
| `spring-boot-starter-test` | 测试（JUnit + Mockito） |
| `spring-boot-starter-aop` | AOP |
| `spring-boot-starter-actuator` | 监控 |

**自定义 Starter 步骤：**

```java
// 1. 自动配置类
@Configuration
@ConditionalOnClass(MyService.class)
@EnableConfigurationProperties(MyProperties.class)
public class MyAutoConfiguration {
    
    @Autowired
    private MyProperties properties;
    
    @Bean
    @ConditionalOnMissingBean
    public MyService myService() {
        return new MyService(properties.getPrefix());
    }
}

// 2. 属性配置类
@ConfigurationProperties(prefix = "my.starter")
public class MyProperties {
    private String prefix = "default";
    // getter/setter
}

// 3. spring.factories 文件
// META-INF/spring.factories
// org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
// com.example.MyAutoConfiguration
```

---

**Q5：Spring Boot 支持哪些内嵌服务器？如何切换？**

**答：**

| 服务器 | Starter | 默认 |
|-------|---------|------|
| Tomcat | `spring-boot-starter-tomcat` | 是 |
| Jetty | `spring-boot-starter-jetty` | 否 |
| Undertow | `spring-boot-starter-undertow` | 否 |

**切换方式：**

```xml
<!-- pom.xml：排除 Tomcat，引入 Jetty -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <exclusions>
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-tomcat</artifactId>
        </exclusion>
    </exclusions>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-jetty</artifactId>
</dependency>
```

---

## 二、自动配置原理

**Q6：Spring Boot 的自动配置原理是什么？**

**答：**
自动配置是 Spring Boot 的核心机制，通过 `@EnableAutoConfiguration` 触发。

**核心流程：**

```text
@SpringBootApplication
  └── @EnableAutoConfiguration
        └── @Import(AutoConfigurationImportSelector.class)
              └── 读取 META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
                    └── 加载所有自动配置类
                          └── 使用 @Conditional 注解按条件装配
```

**关键注解：**

| 条件注解 | 说明 |
|---------|------|
| `@ConditionalOnClass` | 类路径存在指定类时才生效 |
| `@ConditionalOnMissingClass` | 类路径不存在指定类时才生效 |
| `@ConditionalOnBean` | 容器中存在指定 Bean 时才生效 |
| `@ConditionalOnMissingBean` | 容器中不存在指定 Bean 时才生效 |
| `@ConditionalOnProperty` | 配置文件存在指定属性时才生效 |
| `@ConditionalOnResource` | 类路径存在指定资源时才生效 |
| `@ConditionalOnWebApplication` | 当前是 Web 应用时才生效 |

**示例：WebMvc 自动配置**
```java
@AutoConfiguration
@ConditionalOnWebApplication(type = Type.SERVLET)
@ConditionalOnClass({Servlet.class, DispatcherServlet.class, WebMvcConfigurer.class})
@ConditionalOnMissingBean(WebMvcConfigurationSupport.class)
public class WebMvcAutoConfiguration {
    // 自动配置 Spring MVC
}
```

---

**Q7：如何禁用某个自动配置类？**

**答：**

**方式一：通过 exclude 属性**
```java
@SpringBootApplication(exclude = {
    DataSourceAutoConfiguration.class,
    SecurityAutoConfiguration.class
})
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

**方式二：通过配置文件**
```properties
# application.properties
spring.autoconfigure.exclude=org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration
```

**方式三：通过 @ConditionalOnProperty**
```java
@Configuration
@ConditionalOnProperty(name = "my.feature.enabled", havingValue = "true")
public class MyAutoConfiguration {
    // 只有当 my.feature.enabled=true 时才生效
}
```

---

**Q8：Spring Boot 如何实现多模块的自动配置？**

**答：**
多模块项目可以通过自定义 Starter 实现自动配置隔离。

**项目结构：**
```text
my-project/
├── my-spring-boot-starter/
│   ├── src/main/java/com/example/
│   │   ├── MyAutoConfiguration.java
│   │   └── MyProperties.java
│   └── src/main/resources/META-INF/spring/
│       └── org.springframework.boot.autoconfigure.AutoConfiguration.imports
├── module-a/
│   └── ...
└── module-b/
    └── ...
```

**AutoConfiguration.imports 文件：**
```text
com.example.autoconfigure.MyAutoConfiguration
com.example.autoconfigure.AnotherAutoConfiguration
```

---

**Q9：Spring Boot 3.x 自动配置机制有哪些变化？**

**答：**

| 特性 | Spring Boot 2.x | Spring Boot 3.x |
|-----|----------------|-----------------|
| 配置文件 | `spring.factories` | `AutoConfiguration.imports` |
| 配置位置 | `META-INF/spring.factories` | `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` |
| 格式 | 键值对 | 每行一个全限定类名 |
| 自动配置类 | 需 `@Configuration` | 需 `@AutoConfiguration`（新注解） |

**Spring Boot 3.x 配置格式：**
```text
# META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
com.example.autoconfigure.MyAutoConfiguration
com.example.autoconfigure.AnotherAutoConfiguration
```

---

## 三、依赖注入与 IoC 容器

**Q10：Spring 中 `@Autowired` 和 `@Resource` 有什么区别？**

**答：**

| 对比维度 | @Autowired | @Resource |
|---------|-----------|-----------|
| 来源 | Spring 框架 | JDK（javax.annotation） |
| 注入方式 | 默认 byType | 默认 byName |
| 是否必须 | 默认 required=true | 默认必须 |
| 配合注解 | @Qualifier | @Resource(name="xxx") |

```java
@Service
public class UserService {
    
    // @Autowired：按类型注入
    @Autowired
    private UserRepository userRepository;
    
    // @Autowired + @Qualifier：按名称注入
    @Autowired
    @Qualifier("mysqlUserDao")
    private UserDao userDao;
    
    // @Resource：默认按名称，找不到再按类型
    @Resource(name = "mysqlUserDao")
    private UserDao userDao2;
}
```

---

**Q11：Spring 中有哪些注入方式？**

**答：**

| 注入方式 | 说明 | 推荐程度 |
|---------|------|---------|
| 构造器注入 | 通过构造方法注入 | ⭐⭐⭐⭐⭐（最推荐） |
| Setter 注入 | 通过 setter 方法注入 | ⭐⭐⭐ |
| 字段注入 | 通过 `@Autowired` 直接注入字段 | ⭐⭐ |

```java
@Service
public class UserService {
    
    // 方式一：字段注入（不推荐：不利于测试，隐藏依赖）
    @Autowired
    private UserRepository userRepository;
    
    // 方式二：Setter 注入
    private RoleRepository roleRepository;
    
    @Autowired
    public void setRoleRepository(RoleRepository roleRepository) {
        this.roleRepository = roleRepository;
    }
    
    // 方式三：构造器注入（推荐：不可变，依赖明确，便于测试）
    private final PermissionRepository permissionRepository;
    
    public UserService(PermissionRepository permissionRepository) {
        this.permissionRepository = permissionRepository;
    }
    
    // Lombok 简化构造器注入
    // @RequiredArgsConstructor
    // private final UserRepository userRepository;
}
```

---

**Q12：Spring Bean 的作用域有哪些？**

**答：**

| 作用域 | 说明 | 使用场景 |
|-------|------|---------|
| **singleton** | 默认，整个容器只有一个实例 | 无状态 Bean（Service、DAO） |
| **prototype** | 每次获取都创建新实例 | 有状态 Bean |
| **request** | 每个 HTTP 请求一个实例 | Web 应用 |
| **session** | 每个 HTTP 会话一个实例 | Web 应用 |
| **application** | 每个 ServletContext 一个实例 | Web 应用 |
| **websocket** | 每个 WebSocket 会话一个实例 | WebSocket |

```java
@Component
@Scope("prototype")  // 每次获取创建新实例
public class PrototypeBean {
    // ...
}

// 或者使用常量
@Component
@Scope(ConfigurableBeanFactory.SCOPE_PROTOTYPE)
public class PrototypeBean {
    // ...
}
```

---

**Q13：Spring Bean 的生命周期是怎样的？**

**答：**

```text
1. 实例化（Instantiation）
   └── 通过构造器创建 Bean 实例

2. 属性赋值（Populate Properties）
   └── 依赖注入、@Value 赋值

3. 初始化前（BeanNameAware、BeanFactoryAware、ApplicationContextAware）
   └── 回调 Aware 接口

4. 初始化前处理（BeanPostProcessor.postProcessBeforeInitialization）
   └── @PostConstruct 方法在此执行

5. 初始化（InitializingBean.afterPropertiesSet 或 init-method）

6. 初始化后处理（BeanPostProcessor.postProcessAfterInitialization）
   └── AOP 代理在此生成

7. Bean 就绪（Ready to Use）

8. 销毁前（@PreDestroy 或 DisposableBean.destroy 或 destroy-method）
```

```java
@Component
public class MyBean implements InitializingBean, DisposableBean {
    
    @PostConstruct
    public void postConstruct() {
        System.out.println("5. @PostConstruct 方法");
    }
    
    @Override
    public void afterPropertiesSet() {
        System.out.println("6. InitializingBean 接口");
    }
    
    @PreDestroy
    public void preDestroy() {
        System.out.println("8. @PreDestroy 方法");
    }
    
    @Override
    public void destroy() {
        System.out.println("8. DisposableBean 接口");
    }
}
```

---

**Q14：Spring 中有哪些注册 Bean 的方式？**

**答：**

| 方式 | 说明 | 示例 |
|-----|------|------|
| `@Component` | 组件扫描 | `@Component` |
| `@Service` | 服务层 | `@Service` |
| `@Repository` | 数据访问层 | `@Repository` |
| `@Controller` | 控制器 | `@Controller` |
| `@Bean` | 方法级别声明 | `@Bean` 在 `@Configuration` 类中 |
| `@Import` | 导入其他配置类 | `@Import(OtherConfig.class)` |
| `FactoryBean` | 工厂模式创建 Bean | 实现 `FactoryBean<T>` 接口 |

```java
@Configuration
public class AppConfig {
    
    // @Bean 方式
    @Bean
    public DataSource dataSource() {
        return new HikariDataSource();
    }
    
    // 条件 Bean
    @Bean
    @ConditionalOnProperty(name = "cache.enabled", havingValue = "true")
    public CacheManager cacheManager() {
        return new ConcurrentMapCacheManager();
    }
    
    // 带参数的 Bean
    @Bean
    public UserService userService(UserRepository userRepository) {
        return new UserService(userRepository);
    }
}
```

---

## 四、配置管理

**Q15：Spring Boot 支持哪些配置文件格式？优先级如何？**

**答：**

**支持格式：** `.properties`、`.yml`/`.yaml`

**配置优先级（从高到低）：**

| 优先级 | 来源 |
|-------|------|
| 1 | 命令行参数 `--server.port=8080` |
| 2 | `SPRING_APPLICATION_JSON` 环境变量 |
| 3 | Servlet 初始化参数 |
| 4 | JNDI 属性 |
| 5 | Java 系统属性 `System.getProperties()` |
| 6 | 操作系统环境变量 |
| 7 | `application-{profile}.properties`（外部） |
| 8 | `application-{profile}.properties`（内部） |
| 9 | `application.properties`（外部） |
| 10 | `application.properties`（内部） |
| 11 | `@PropertySource` 注解 |
| 12 | 默认属性 |

**外部配置文件位置（优先级从高到低）：**
```text
1. jar 包同级目录的 config/ 子目录
2. jar 包同级目录
3. classpath 中的 config/ 包
4. classpath 根路径
```

---

**Q16：properties 和 yml 配置如何选择？多环境配置如何实现？**

**答：**

| 对比 | properties | yml |
|-----|-----------|-----|
| 语法 | 键值对 | 层级缩进 |
| 可读性 | 一般 | 好（层次清晰） |
| 列表 | 不支持 | 支持 |
| 复杂配置 | 繁琐 | 简洁 |

**多环境配置：**

```yaml
# application.yml（公共配置）
spring:
  application:
    name: my-app

# application-dev.yml（开发环境）
server:
  port: 8080
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/dev_db

# application-prod.yml（生产环境）
server:
  port: 80
spring:
  datasource:
    url: jdbc:mysql://prod-server:3306/prod_db
```

**激活环境：**
```properties
# application.properties
spring.profiles.active=dev
```
```bash
# 命令行
java -jar app.jar --spring.profiles.active=prod
```

---

**Q17：`@Value` 和 `@ConfigurationProperties` 有什么区别？**

**答：**

| 对比 | @Value | @ConfigurationProperties |
|-----|--------|-------------------------|
| 绑定方式 | 单个属性 | 批量绑定 |
| 松散绑定 | 不支持 | 支持（user-name → userName） |
| JSR303 校验 | 不支持 | 支持 `@Validated` |
| 复杂类型 | 不支持 | 支持 List、Map 等 |
| 使用场景 | 单个属性 | 一组相关属性 |

```java
// @ConfigurationProperties（推荐）
@Component
@ConfigurationProperties(prefix = "app")
@Validated
public class AppProperties {
    @NotBlank
    private String name;
    private String version;
    private List<String> authors;
    private Map<String, String> settings;
    // getter/setter
}

// 配置文件
// app.name=MyApp
// app.version=1.0.0
// app.authors[0]=张三
// app.settings.key1=value1

// 使用
@RestController
public class ConfigController {
    @Autowired
    private AppProperties appProperties;
    
    @GetMapping("/config")
    public AppProperties getConfig() {
        return appProperties;
    }
}
```

---

**Q18：Spring Boot 如何实现配置热更新？**

**答：**

**方案一：Spring Cloud Config + Bus**
```yaml
spring:
  cloud:
    config:
      uri: http://config-server:8888
    bus:
      enabled: true
```

```java
@RestController
@RefreshScope  // 标记需要刷新的 Bean
public class ConfigController {
    @Value("${app.message}")
    private String message;
    
    @GetMapping("/message")
    public String getMessage() {
        return message;
    }
}
```

**方案二：Nacos 配置中心**
```yaml
spring:
  cloud:
    nacos:
      config:
        server-addr: localhost:8848
        file-extension: yaml
```

**方案三：使用 Apollo 配置中心**
```java
@Configuration
public class ApolloConfig {
    @Value("${timeout:3000}")
    private int timeout;
}
```

---

## 五、AOP 面向切面编程

**Q19：什么是 AOP？Spring AOP 的代理机制是什么？**

**答：**
AOP（Aspect-Oriented Programming）通过预编译和运行时动态代理，在不修改源码的情况下增强功能。

**代理机制：**

| 代理方式 | 条件 | 说明 |
|---------|------|------|
| JDK 动态代理 | 目标类实现了接口 | 基于接口，`Proxy.newProxyInstance()` |
| CGLIB 代理 | 目标类没有实现接口 | 基于继承，生成子类 |

**Spring Boot 2.x 默认：** 接口用 JDK 代理，无接口用 CGLIB
**Spring Boot 3.x 默认：** 始终使用 CGLIB

```properties
# 强制使用 CGLIB
spring.aop.proxy-target-class=true
```

**AOP 核心概念：**

| 术语 | 说明 |
|-----|------|
| Aspect（切面） | 横切关注点的模块化，如日志、事务 |
| JoinPoint（连接点） | 程序执行过程中的某个点，如方法调用 |
| Advice（通知） | 在切面中执行的代码 |
| Pointcut（切入点） | 匹配连接点的表达式 |
| Target（目标对象） | 被代理的对象 |

---

**Q20：AOP 有哪些通知类型？如何实现？**

**答：**

| 通知类型 | 注解 | 执行时机 |
|---------|------|---------|
| 前置通知 | `@Before` | 目标方法执行前 |
| 后置通知 | `@After` | 目标方法执行后（无论是否异常） |
| 返回通知 | `@AfterReturning` | 目标方法正常返回后 |
| 异常通知 | `@AfterThrowing` | 目标方法抛出异常后 |
| 环绕通知 | `@Around` | 目标方法执行前后（最强大） |

```java
@Aspect
@Component
@Slf4j
public class LogAspect {
    
    // 切入点定义
    @Pointcut("execution(* com.example.service.*.*(..))")
    public void serviceLayer() {}
    
    // 前置通知
    @Before("serviceLayer()")
    public void before(JoinPoint joinPoint) {
        String methodName = joinPoint.getSignature().getName();
        Object[] args = joinPoint.getArgs();
        log.info("方法 {} 开始执行，参数: {}", methodName, args);
    }
    
    // 返回通知
    @AfterReturning(value = "serviceLayer()", returning = "result")
    public void afterReturning(JoinPoint joinPoint, Object result) {
        log.info("方法 {} 执行完成，返回值: {}", joinPoint.getSignature().getName(), result);
    }
    
    // 异常通知
    @AfterThrowing(value = "serviceLayer()", throwing = "ex")
    public void afterThrowing(JoinPoint joinPoint, Exception ex) {
        log.error("方法 {} 执行异常: {}", joinPoint.getSignature().getName(), ex.getMessage());
    }
    
    // 环绕通知
    @Around("serviceLayer()")
    public Object around(ProceedingJoinPoint joinPoint) throws Throwable {
        long start = System.currentTimeMillis();
        String methodName = joinPoint.getSignature().getName();
        
        log.info("环绕通知 - 方法 {} 开始执行", methodName);
        
        try {
            Object result = joinPoint.proceed();  // 执行目标方法
            long elapsed = System.currentTimeMillis() - start;
            log.info("环绕通知 - 方法 {} 执行完成，耗时: {}ms", methodName, elapsed);
            return result;
        } catch (Exception e) {
            log.error("环绕通知 - 方法 {} 执行异常: {}", methodName, e.getMessage());
            throw e;
        }
    }
}
```

---

**Q21：AOP 可以实现哪些实际功能？**

**答：**

**1. 统一日志记录**
```java
@Aspect
@Component
public class WebLogAspect {
    @Pointcut("@annotation(org.springframework.web.bind.annotation.RequestMapping)")
    public void requestMapping() {}
    
    @Around("requestMapping()")
    public Object logRequest(ProceedingJoinPoint joinPoint) throws Throwable {
        HttpServletRequest request = ((ServletRequestAttributes) 
            RequestContextHolder.getRequestAttributes()).getRequest();
        
        log.info("URL: {}, Method: {}, IP: {}", 
            request.getRequestURL(), request.getMethod(), request.getRemoteAddr());
        
        Object result = joinPoint.proceed();
        log.info("Response: {}", result);
        return result;
    }
}
```

**2. 接口限流**
```java
@Aspect
@Component
public class RateLimitAspect {
    private final Map<String, AtomicInteger> counter = new ConcurrentHashMap<>();
    
    @Around("@annotation(rateLimit)")
    public Object rateLimit(ProceedingJoinPoint joinPoint, RateLimit rateLimit) 
            throws Throwable {
        String key = joinPoint.getSignature().toShortString();
        AtomicInteger count = counter.computeIfAbsent(key, k -> new AtomicInteger(0));
        
        if (count.incrementAndGet() > rateLimit.value()) {
            throw new RuntimeException("请求过于频繁，请稍后再试");
        }
        
        return joinPoint.proceed();
    }
}
```

**3. 权限校验**
```java
@Aspect
@Component
public class PermissionAspect {
    @Around("@annotation(requirePermission)")
    public Object checkPermission(ProceedingJoinPoint joinPoint, 
            RequirePermission requirePermission) throws Throwable {
        String currentUser = getCurrentUser();
        String requiredRole = requirePermission.value();
        
        if (!hasPermission(currentUser, requiredRole)) {
            throw new AccessDeniedException("无权限访问");
        }
        
        return joinPoint.proceed();
    }
}
```

---

## 六、数据访问与事务管理

**Q22：Spring Boot 如何整合 MyBatis？**

**答：**

**方式一：注解方式**
```java
@Mapper
public interface UserMapper {
    @Select("SELECT * FROM user WHERE id = #{id}")
    User findById(Long id);
    
    @Insert("INSERT INTO user(name, age) VALUES(#{name}, #{age})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(User user);
    
    @Update("UPDATE user SET name = #{name} WHERE id = #{id}")
    int update(User user);
    
    @Delete("DELETE FROM user WHERE id = #{id}")
    int delete(Long id);
}
```

**方式二：XML 方式**
```xml
<!-- resources/mapper/UserMapper.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
    "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.example.mapper.UserMapper">
    <select id="findById" resultType="com.example.entity.User">
        SELECT * FROM user WHERE id = #{id}
    </select>
    
    <insert id="insert" useGeneratedKeys="true" keyProperty="id">
        INSERT INTO user(name, age) VALUES(#{name}, #{age})
    </insert>
</mapper>
```

**配置：**
```yaml
# application.yml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb?useSSL=false&serverTimezone=Asia/Shanghai
    username: root
    password: 123456
    driver-class-name: com.mysql.cj.jdbc.Driver

mybatis:
  mapper-locations: classpath:mapper/*.xml
  type-aliases-package: com.example.entity
  configuration:
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
```

---

**Q23：Spring 事务管理是如何实现的？`@Transactional` 失效的场景有哪些？**

**答：**

**事务实现原理：**
- 基于 AOP 代理，通过 `TransactionInterceptor` 拦截
- 底层使用 `PlatformTransactionManager` 管理事务

**`@Transactional` 失效场景：**

| 场景 | 原因 | 解决方案 |
|-----|------|---------|
| 非 public 方法 | CGLIB 代理无法代理私有方法 | 改为 public |
| 同类方法调用 | 不经过代理，直接调用 | 注入自身或拆分到不同类 |
| 异常被捕获 | 事务只对未捕获的 RuntimeException 回滚 | 抛出异常或手动回滚 |
| 非 RuntimeException | 默认只对 RuntimeException 回滚 | 设置 `rollbackFor = Exception.class` |
| 数据库引擎不支持 | MyISAM 不支持事务 | 使用 InnoDB |
| 多线程 | 事务绑定到线程 | 使用分布式事务 |

```java
@Service
public class UserService {
    
    @Autowired
    private UserService self;  // 注入自身解决同类调用失效
    
    @Transactional
    public void methodA() {
        // 错误：同类方法调用，事务不生效
        this.methodB();
        
        // 正确：通过代理调用
        self.methodB();
    }
    
    @Transactional(rollbackFor = Exception.class)  // 所有异常都回滚
    public void methodB() {
        // ...
    }
    
    @Transactional
    public void methodC() {
        try {
            // 数据库操作
        } catch (Exception e) {
            // 错误：捕获了异常，事务不会回滚
            // 正确：手动回滚
            TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();
            throw e;  // 或者抛出异常
        }
    }
}
```

---

**Q24：Spring 事务的传播行为有哪些？**

**答：**

| 传播行为 | 说明 |
|---------|------|
| **REQUIRED**（默认） | 加入当前事务，没有则创建新事务 |
| **REQUIRES_NEW** | 创建新事务，挂起当前事务 |
| **SUPPORTS** | 加入当前事务，没有则以非事务方式运行 |
| **NOT_SUPPORTED** | 以非事务方式运行，挂起当前事务 |
| **MANDATORY** | 必须存在事务，否则抛异常 |
| **NEVER** | 以非事务方式运行，存在事务则抛异常 |
| **NESTED** | 嵌套事务，内层事务可独立回滚 |

```java
@Service
public class OrderService {
    
    @Transactional(propagation = Propagation.REQUIRED)
    public void createOrder() {
        // 当前事务
        
        // 创建新事务，独立提交
        paymentService.pay();
        
        // 如果这里抛出异常，createOrder 回滚，但 pay 不会回滚
    }
}

@Service
public class PaymentService {
    
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void pay() {
        // 独立的新事务
    }
}
```

---

**Q25：Spring Boot 如何整合 JPA？**

**答：**

```java
// 实体类
@Entity
@Table(name = "user")
@Data
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, length = 50)
    private String name;
    
    private Integer age;
    
    @Column(name = "create_time")
    private LocalDateTime createTime;
    
    @PrePersist
    public void prePersist() {
        this.createTime = LocalDateTime.now();
    }
}

// Repository 接口
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    // 方法命名查询
    List<User> findByName(String name);
    List<User> findByAgeGreaterThan(Integer age);
    User findByNameAndAge(String name, Integer age);
    
    // JPQL 查询
    @Query("SELECT u FROM User u WHERE u.age > :age")
    List<User> findUsersOlderThan(@Param("age") Integer age);
    
    // 原生 SQL 查询
    @Query(value = "SELECT * FROM user WHERE name = ?1", nativeQuery = true)
    List<User> findByNativeQuery(String name);
    
    // 分页查询
    Page<User> findByAge(Integer age, Pageable pageable);
}
```

---

**Q26：如何实现多数据源配置？**

**答：**

```yaml
# application.yml
spring:
  datasource:
    primary:
      url: jdbc:mysql://localhost:3306/primary_db
      username: root
      password: 123456
    secondary:
      url: jdbc:mysql://localhost:3306/secondary_db
      username: root
      password: 123456
```

```java
@Configuration
public class DataSourceConfig {
    
    @Primary
    @Bean(name = "primaryDataSource")
    @ConfigurationProperties(prefix = "spring.datasource.primary")
    public DataSource primaryDataSource() {
        return DataSourceBuilder.create().build();
    }
    
    @Bean(name = "secondaryDataSource")
    @ConfigurationProperties(prefix = "spring.datasource.secondary")
    public DataSource secondaryDataSource() {
        return DataSourceBuilder.create().build();
    }
    
    @Primary
    @Bean(name = "primaryTransactionManager")
    public DataSourceTransactionManager primaryTransactionManager(
            @Qualifier("primaryDataSource") DataSource dataSource) {
        return new DataSourceTransactionManager(dataSource);
    }
    
    @Bean(name = "secondaryTransactionManager")
    public DataSourceTransactionManager secondaryTransactionManager(
            @Qualifier("secondaryDataSource") DataSource dataSource) {
        return new DataSourceTransactionManager(dataSource);
    }
}
```

---

## 七、RESTful API 设计

**Q27：Spring Boot 中常用的请求映射注解有哪些？**

**答：**

| 注解 | 说明 | HTTP 方法 |
|-----|------|----------|
| `@RequestMapping` | 通用请求映射 | 所有方法 |
| `@GetMapping` | 查询资源 | GET |
| `@PostMapping` | 创建资源 | POST |
| `@PutMapping` | 更新资源（全量） | PUT |
| `@PatchMapping` | 更新资源（部分） | PATCH |
| `@DeleteMapping` | 删除资源 | DELETE |

```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @GetMapping
    public List<User> list(@RequestParam(required = false) String name) {
        // GET /api/users?name=张三
    }
    
    @GetMapping("/{id}")
    public User getById(@PathVariable Long id) {
        // GET /api/users/1
    }
    
    @PostMapping
    public User create(@Valid @RequestBody User user) {
        // POST /api/users
    }
    
    @PutMapping("/{id}")
    public User update(@PathVariable Long id, @Valid @RequestBody User user) {
        // PUT /api/users/1
    }
    
    @DeleteMapping("/{id}")
    public void delete(@PathVariable Long id) {
        // DELETE /api/users/1
    }
}
```

---

**Q28：RESTful API 设计有哪些最佳实践？**

**答：**

**1. URL 设计规范：**
```text
# 资源命名：名词复数
GET    /api/users          # 获取用户列表
GET    /api/users/1        # 获取用户详情
POST   /api/users          # 创建用户
PUT    /api/users/1        # 更新用户
DELETE /api/users/1        # 删除用户

# 关联资源
GET    /api/users/1/orders # 获取用户订单
```

**2. 状态码使用：**
```java
@RestController
public class UserController {
    
    @PostMapping("/users")
    @ResponseStatus(HttpStatus.CREATED)  // 201
    public User create(@RequestBody User user) {
        return userService.create(user);
    }
    
    @GetMapping("/users/{id}")
    public ResponseEntity<User> getById(@PathVariable Long id) {
        return userService.findById(id)
            .map(ResponseEntity::ok)              // 200
            .orElse(ResponseEntity.notFound().build());  // 404
    }
}
```

**3. 分页和排序：**
```java
@GetMapping("/users")
public Page<User> list(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "10") int size,
        @RequestParam(defaultValue = "id") String sort) {
    Pageable pageable = PageRequest.of(page, size, Sort.by(sort));
    return userService.findAll(pageable);
}
```

**4. 版本控制：**
```java
// URL 版本
@GetMapping("/api/v1/users")
@GetMapping("/api/v2/users")

// Header 版本
@GetMapping(value = "/api/users", headers = "API-Version=1")
```

---

**Q29：Spring Boot 如何处理请求参数校验？**

**答：**

```java
// 实体类校验注解
@Data
public class UserDTO {
    @NotNull(message = "ID 不能为空", groups = Update.class)
    private Long id;
    
    @NotBlank(message = "姓名不能为空")
    @Size(min = 2, max = 20, message = "姓名长度需要在 2-20 之间")
    private String name;
    
    @Min(value = 0, message = "年龄不能小于 0")
    @Max(value = 150, message = "年龄不能大于 150")
    private Integer age;
    
    @Email(message = "邮箱格式不正确")
    private String email;
    
    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式不正确")
    private String phone;
    
    // 分组接口
    public interface Update {}
}

// 控制器中使用
@RestController
public class UserController {
    
    @PostMapping("/users")
    public Result create(@Valid @RequestBody UserDTO user) {
        // 自动校验
    }
    
    @PutMapping("/users")
    public Result update(@Validated(UserDTO.Update.class) @RequestBody UserDTO user) {
        // 仅校验 Update 分组
    }
}

// 全局异常处理
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public Result handleValidation(MethodArgumentNotValidException ex) {
        String message = ex.getBindingResult().getFieldErrors().stream()
            .map(FieldError::getDefaultMessage)
            .collect(Collectors.joining(", "));
        return Result.error(400, message);
    }
}
```

---

## 八、安全认证与授权

**Q30：Spring Security 的核心原理是什么？**

**答：**
Spring Security 通过**过滤器链（Filter Chain）** 实现认证和授权。

**核心流程：**
```text
请求 → SecurityFilterChain（过滤器链）
  ├── UsernamePasswordAuthenticationFilter（认证）
  ├── BasicAuthenticationFilter
  ├── ExceptionTranslationFilter
  └── FilterSecurityInterceptor（授权）
```

**核心组件：**

| 组件 | 作用 |
|-----|------|
| `SecurityContextHolder` | 存储当前认证信息 |
| `Authentication` | 认证信息对象 |
| `UserDetailsService` | 加载用户详情 |
| `GrantedAuthority` | 用户权限 |
| `AuthenticationManager` | 认证管理器 |
| `AccessDecisionManager` | 授权决策器 |

---

**Q31：Spring Boot 中如何实现 JWT 认证？**

**答：**

```java
// 1. JWT 工具类
@Component
public class JwtUtils {
    @Value("${jwt.secret}")
    private String secret;
    
    @Value("${jwt.expiration}")
    private long expiration;
    
    // 生成 Token
    public String generateToken(String username) {
        return Jwts.builder()
            .setSubject(username)
            .setIssuedAt(new Date())
            .setExpiration(new Date(System.currentTimeMillis() + expiration))
            .signWith(Keys.hmacShaKeyFor(secret.getBytes()))
            .compact();
    }
    
    // 解析 Token
    public String getUsernameFromToken(String token) {
        return Jwts.parserBuilder()
            .setSigningKey(Keys.hmacShaKeyFor(secret.getBytes()))
            .build()
            .parseClaimsJws(token)
            .getBody()
            .getSubject();
    }
    
    // 验证 Token
    public boolean validateToken(String token) {
        try {
            Jwts.parserBuilder()
                .setSigningKey(Keys.hmacShaKeyFor(secret.getBytes()))
                .build()
                .parseClaimsJws(token);
            return true;
        } catch (JwtException e) {
            return false;
        }
    }
}

// 2. JWT 过滤器
@Component
public class JwtFilter extends OncePerRequestFilter {
    @Autowired
    private JwtUtils jwtUtils;
    
    @Override
    protected void doFilterInternal(HttpServletRequest request,
            HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        
        String authHeader = request.getHeader("Authorization");
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);
            if (jwtUtils.validateToken(token)) {
                String username = jwtUtils.getUsernameFromToken(token);
                UsernamePasswordAuthenticationToken authentication =
                    new UsernamePasswordAuthenticationToken(username, null, null);
                SecurityContextHolder.getContext().setAuthentication(authentication);
            }
        }
        chain.doFilter(request, response);
    }
}

// 3. Security 配置
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Autowired
    private JwtFilter jwtFilter;
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.csrf().disable()
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .sessionManagement(session -> 
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);
        
        return http.build();
    }
}
```

---

**Q32：Spring Security 中如何实现权限控制？**

**答：**

**方式一：注解方式**
```java
@RestController
@RequestMapping("/api")
public class AdminController {
    
    @PreAuthorize("hasRole('ADMIN')")
    @GetMapping("/admin")
    public String admin() {
        return "admin page";
    }
    
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER')")
    @GetMapping("/manage")
    public String manage() {
        return "manage page";
    }
    
    @PreAuthorize("hasAuthority('user:delete')")
    @DeleteMapping("/users/{id}")
    public void deleteUser(@PathVariable Long id) {
        // 需要有 user:delete 权限
    }
}

// 开启方法级别权限控制
@Configuration
@EnableGlobalMethodSecurity(prePostEnabled = true)
public class MethodSecurityConfig {
}
```

**方式二：RBAC 权限模型**
```java
// 用户表
@Entity
public class User {
    @Id private Long id;
    private String username;
    private String password;
    
    @ManyToMany(fetch = FetchType.EAGER)
    private Set<Role> roles;
}

// 角色表
@Entity
public class Role {
    @Id private Long id;
    private String name;
    
    @ManyToMany(fetch = FetchType.EAGER)
    private Set<Permission> permissions;
}

// 权限表
@Entity
public class Permission {
    @Id private Long id;
    private String name;  // 如 user:read, user:delete
    private String url;
}
```

---

## 九、异常处理与统一响应

**Q33：Spring Boot 如何实现全局异常处理？**

**答：**

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    // 处理业务异常
    @ExceptionHandler(BusinessException.class)
    public Result handleBusinessException(BusinessException e) {
        return Result.error(e.getCode(), e.getMessage());
    }
    
    // 处理参数校验异常
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public Result handleValidationException(MethodArgumentNotValidException e) {
        String message = e.getBindingResult().getFieldErrors().stream()
            .map(FieldError::getDefaultMessage)
            .collect(Collectors.joining(", "));
        return Result.error(400, message);
    }
    
    // 处理未找到资源异常
    @ExceptionHandler(NoHandlerFoundException.class)
    public Result handleNotFound(NoHandlerFoundException e) {
        return Result.error(404, "资源不存在");
    }
    
    // 处理其他异常
    @ExceptionHandler(Exception.class)
    public Result handleException(Exception e) {
        log.error("系统异常", e);
        return Result.error(500, "系统内部错误");
    }
}
```

---

**Q34：如何设计统一的响应格式？**

**答：**

```java
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Result<T> {
    private Integer code;
    private String message;
    private T data;
    private Long timestamp;
    
    public static <T> Result<T> success(T data) {
        return new Result<>(200, "success", data, System.currentTimeMillis());
    }
    
    public static <T> Result<T> success() {
        return success(null);
    }
    
    public static <T> Result<T> error(Integer code, String message) {
        return new Result<>(code, message, null, System.currentTimeMillis());
    }
}

// 统一响应增强
@RestControllerAdvice
public class ResponseAdvice implements ResponseBodyAdvice<Object> {
    
    @Override
    public boolean supports(MethodParameter returnType, Class converterType) {
        return !returnType.getParameterType().equals(Result.class);
    }
    
    @Override
    public Object beforeBodyWrite(Object body, MethodParameter returnType,
            MediaType selectedContentType, Class selectedConverterType,
            ServerHttpRequest request, ServerHttpResponse response) {
        if (body instanceof String) {
            return JSON.toJSONString(Result.success(body));
        }
        return Result.success(body);
    }
}
```

---

## 十、微服务与集成

**Q35：Spring Cloud 和 Spring Boot 有什么关系？**

**答：**

| 对比 | Spring Boot | Spring Cloud |
|-----|------------|-------------|
| 定位 | 快速开发单个微服务 | 微服务治理框架 |
| 功能 | 自动配置、起步依赖 | 服务发现、配置中心、网关 |
| 依赖 | 独立运行 | 基于 Spring Boot |
| 使用 | 开发单个服务 | 管理多个服务 |

**Spring Cloud 核心组件：**

| 组件 | 功能 |
|-----|------|
| Eureka / Nacos | 服务注册与发现 |
| Ribbon / LoadBalancer | 客户端负载均衡 |
| OpenFeign | 声明式 HTTP 调用 |
| Gateway | API 网关 |
| Config / Nacos Config | 配置中心 |
| Sentinel | 熔断降级 |
| Sleuth + Zipkin | 链路追踪 |

---

**Q36：Spring Boot 中如何实现服务间调用？**

**答：**

**方式一：RestTemplate**
```java
@Configuration
public class RestTemplateConfig {
    @Bean
    @LoadBalanced  // 启用负载均衡
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}

@Service
public class OrderService {
    @Autowired
    private RestTemplate restTemplate;
    
    public User getUser(Long userId) {
        String url = "http://user-service/api/users/" + userId;
        return restTemplate.getForObject(url, User.class);
    }
}
```

**方式二：OpenFeign（推荐）**
```java
@FeignClient(name = "user-service", path = "/api/users")
public interface UserFeignClient {
    
    @GetMapping("/{id}")
    User getUserById(@PathVariable Long id);
    
    @PostMapping
    User createUser(@RequestBody User user);
}

@Service
public class OrderService {
    @Autowired
    private UserFeignClient userFeignClient;
    
    public Order createOrder(Long userId) {
        User user = userFeignClient.getUserById(userId);
        // ...
    }
}
```

---

**Q37：Spring Boot 如何整合消息队列？**

**答：**

**整合 RabbitMQ：**
```yaml
spring:
  rabbitmq:
    host: localhost
    port: 5672
    username: guest
    password: guest
```

```java
// 生产者
@Component
public class MessageProducer {
    @Autowired
    private RabbitTemplate rabbitTemplate;
    
    public void sendMessage(String message) {
        rabbitTemplate.convertAndSend("order.exchange", "order.create", message);
    }
}

// 消费者
@Component
public class MessageConsumer {
    
    @RabbitListener(queues = "order.queue")
    public void handleMessage(String message) {
        System.out.println("收到消息: " + message);
    }
}

// 配置
@Configuration
public class RabbitConfig {
    @Bean
    public Queue orderQueue() {
        return new Queue("order.queue", true);
    }
    
    @Bean
    public TopicExchange orderExchange() {
        return new TopicExchange("order.exchange");
    }
    
    @Bean
    public Binding orderBinding() {
        return BindingBuilder.bind(orderQueue())
            .to(orderExchange())
            .with("order.*");
    }
}
```

**整合 Kafka：**
```yaml
spring:
  kafka:
    bootstrap-servers: localhost:9092
    consumer:
      group-id: my-group
```

```java
// 生产者
@Component
public class KafkaProducer {
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;
    
    public void send(String topic, String message) {
        kafkaTemplate.send(topic, message);
    }
}

// 消费者
@Component
public class KafkaConsumer {
    
    @KafkaListener(topics = "order-topic", groupId = "my-group")
    public void listen(String message) {
        System.out.println("收到消息: " + message);
    }
}
```

---

**Q38：Spring Boot 如何实现定时任务？**

**答：**

```java
@Configuration
@EnableScheduling
public class ScheduleConfig {
}

@Component
public class ScheduledTasks {
    
    // 固定延迟（单位：毫秒）
    @Scheduled(fixedDelay = 5000)
    public void taskWithFixedDelay() {
        System.out.println("上次执行结束后 5 秒执行");
    }
    
    // 固定速率（不受上次执行时间影响）
    @Scheduled(fixedRate = 5000)
    public void taskWithFixedRate() {
        System.out.println("每 5 秒执行一次");
    }
    
    // 初始延迟 + 固定速率
    @Scheduled(initialDelay = 10000, fixedRate = 5000)
    public void taskWithInitialDelay() {
        System.out.println("首次延迟 10 秒，之后每 5 秒执行");
    }
    
    // Cron 表达式
    @Scheduled(cron = "0 0 2 * * ?")  // 每天凌晨 2 点
    public void taskWithCron() {
        System.out.println("定时任务执行");
    }
}
```

**Cron 表达式格式：**
```text
秒 分 时 日 月 周
0  0  2  *  *  ?   # 每天凌晨 2 点
0  */5 *  *  *  ?   # 每 5 分钟
0  0  9  ?  *  MON  # 每周一早上 9 点
```

---

## 十一、测试

**Q39：Spring Boot 如何进行单元测试和集成测试？**

**答：**

```java
// 单元测试（不启动 Spring 容器）
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    
    @Mock
    private UserRepository userRepository;
    
    @InjectMocks
    private UserService userService;
    
    @Test
    void testFindById() {
        // 模拟数据
        User mockUser = new User(1L, "张三", 25);
        when(userRepository.findById(1L)).thenReturn(Optional.of(mockUser));
        
        // 执行测试
        User result = userService.findById(1L);
        
        // 验证结果
        assertNotNull(result);
        assertEquals("张三", result.getName());
        verify(userRepository).findById(1L);
    }
}

// 集成测试（启动 Spring 容器）
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureMockMvc
class UserControllerTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @Test
    @Transactional  // 测试后回滚
    void testCreateUser() throws Exception {
        String json = """
            {"name": "张三", "age": 25}
            """;
        
        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(json))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.data.name").value("张三"));
    }
}
```

---

**Q40：Spring Boot 测试中 `@SpringBootTest` 和 `@WebMvcTest` 的区别？**

**答：**

| 注解 | 作用 | 启动范围 |
|-----|------|---------|
| `@SpringBootTest` | 完整集成测试 | 启动完整 Spring 容器 |
| `@WebMvcTest` | 仅测试 Controller 层 | 只加载 Web 层相关 Bean |
| `@DataJpaTest` | 仅测试 JPA 层 | 只加载 JPA 相关 Bean |
| `@JsonTest` | 仅测试 JSON 序列化 | 只加载 JSON 相关 Bean |

```java
// @WebMvcTest：只测试 Controller
@WebMvcTest(UserController.class)
class UserControllerTest {
    @Autowired
    private MockMvc mockMvc;
    
    @MockBean
    private UserService userService;
    
    @Test
    void testGetUser() throws Exception {
        when(userService.findById(1L)).thenReturn(new User(1L, "张三", 25));
        
        mockMvc.perform(get("/api/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data.name").value("张三"));
    }
}

// @DataJpaTest：只测试数据层
@DataJpaTest
class UserRepositoryTest {
    @Autowired
    private TestEntityManager entityManager;
    
    @Autowired
    private UserRepository userRepository;
    
    @Test
    void testFindByName() {
        entityManager.persist(new User("张三", 25));
        List<User> users = userRepository.findByName("张三");
        assertEquals(1, users.size());
    }
}
```

---

## 十二、性能优化与监控

**Q41：Spring Boot Actuator 提供了哪些监控端点？**

**答：**

| 端点 | 说明 | 默认启用 |
|-----|------|---------|
| `/actuator/health` | 健康检查 | 是 |
| `/actuator/info` | 应用信息 | 是 |
| `/actuator/metrics` | 指标信息 | 是 |
| `/actuator/env` | 环境变量 | 否 |
| `/actuator/beans` | 所有 Bean | 否 |
| `/actuator/mappings` | 请求映射 | 否 |
| `/actuator/loggers` | 日志级别 | 否 |
| `/actuator/threaddump` | 线程转储 | 否 |
| `/actuator/heapdump` | 堆转储 | 否 |

```yaml
# application.yml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,env,beans  # 暴露的端点
      base-path: /actuator
  endpoint:
    health:
      show-details: always  # 显示健康检查详情
```

---

**Q42：Spring Boot 如何实现数据库连接池优化？**

**答：**

```yaml
# HikariCP（Spring Boot 默认连接池）
spring:
  datasource:
    hikari:
      maximum-pool-size: 20          # 最大连接数
      minimum-idle: 5                # 最小空闲连接
      idle-timeout: 300000           # 空闲超时（5分钟）
      connection-timeout: 30000      # 连接超时（30秒）
      max-lifetime: 1800000          # 最大生命周期（30分钟）
      pool-name: HikariPool
      connection-test-query: SELECT 1
```

**Druid 连接池：**
```xml
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>druid-spring-boot-starter</artifactId>
    <version>1.2.20</version>
</dependency>
```

```yaml
spring:
  datasource:
    druid:
      initial-size: 5
      min-idle: 5
      max-active: 20
      max-wait: 60000
      stat-view-servlet:
        enabled: true
        url-pattern: /druid/*
      filter:
        stat:
          enabled: true
          log-slow-sql: true
          slow-sql-millis: 1000
```

---

**Q43：Spring Boot 如何优化启动速度？**

**答：**

| 优化方式 | 说明 |
|---------|------|
| 减少不必要的自动配置 | 排除不需要的自动配置类 |
| 使用懒加载 | `spring.main.lazy-initialization=true` |
| 减少 Bean 扫描范围 | 指定 `@ComponentScan` 的包路径 |
| 使用 Spring AOT | Spring Boot 3.0+ 的 AOT 编译 |
| 排除不用的 Starter | 精简 pom.xml 依赖 |

```java
// 排除不需要的自动配置
@SpringBootApplication(exclude = {
    DataSourceAutoConfiguration.class,
    SecurityAutoConfiguration.class
})

// 懒加载
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication app = new SpringApplication(Application.class);
        app.setLazyInitialization(true);
        app.run(args);
    }
}
```

```yaml
# 配置懒加载
spring:
  main:
    lazy-initialization: true
```

---

## 十三、综合实战

**Q44：如何在 Spring Boot 中实现文件上传和下载？**

**答：**

```java
@RestController
@RequestMapping("/api/files")
public class FileController {
    
    @Value("${file.upload-dir}")
    private String uploadDir;
    
    // 单文件上传
    @PostMapping("/upload")
    public Result upload(@RequestParam("file") MultipartFile file) {
        if (file.isEmpty()) {
            return Result.error(400, "文件不能为空");
        }
        
        try {
            String fileName = UUID.randomUUID() + "_" + file.getOriginalFilename();
            File dest = new File(uploadDir + File.separator + fileName);
            file.transferTo(dest);
            return Result.success(fileName);
        } catch (IOException e) {
            return Result.error(500, "上传失败");
        }
    }
    
    // 文件下载
    @GetMapping("/download/{fileName}")
    public ResponseEntity<Resource> download(@PathVariable String fileName) {
        try {
            Path filePath = Paths.get(uploadDir).resolve(fileName).normalize();
            Resource resource = new UrlResource(filePath.toUri());
            
            if (resource.exists()) {
                return ResponseEntity.ok()
                    .header(HttpHeaders.CONTENT_DISPOSITION,
                        "attachment; filename=\"" + resource.getFilename() + "\"")
                    .body(resource);
            }
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }
}

# 配置
spring:
  servlet:
    multipart:
      max-file-size: 10MB
      max-request-size: 10MB
file:
  upload-dir: ./uploads
```

---

**Q45：Spring Boot 如何实现 Redis 缓存？**

**答：**

```java
// 1. 配置
@Configuration
@EnableCaching
public class RedisConfig {
    @Bean
    public RedisCacheManager cacheManager(RedisConnectionFactory factory) {
        RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(30))  // 默认过期时间
            .serializeKeysWith(RedisSerializationContext.SerializationPair
                .fromSerializer(new StringRedisSerializer()))
            .serializeValuesWith(RedisSerializationContext.SerializationPair
                .fromSerializer(new GenericJackson2JsonRedisSerializer()));
        
        return RedisCacheManager.builder(factory)
            .cacheDefaults(config)
            .build();
    }
}

// 2. 使用缓存注解
@Service
public class UserService {
    
    @Cacheable(value = "user", key = "#id")
    public User findById(Long id) {
        // 先从缓存查，缓存不存在则查数据库并写入缓存
        return userRepository.findById(id).orElse(null);
    }
    
    @CachePut(value = "user", key = "#user.id")
    public User update(User user) {
        // 更新数据库，同时更新缓存
        return userRepository.save(user);
    }
    
    @CacheEvict(value = "user", key = "#id")
    public void delete(Long id) {
        // 删除数据库，同时删除缓存
        userRepository.deleteById(id);
    }
    
    @CacheEvict(value = "user", allEntries = true)
    public void clearAllCache() {
        // 清空所有 user 缓存
    }
}
```

---

**Q46：Spring Boot 如何实现异步任务？**

**答：**

```java
@Configuration
@EnableAsync
public class AsyncConfig {
    @Bean
    public Executor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(10);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("async-");
        executor.initialize();
        return executor;
    }
}

@Service
public class AsyncService {
    
    @Async
    public CompletableFuture<String> processTask() {
        try {
            Thread.sleep(3000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        return CompletableFuture.completedFuture("任务完成");
    }
    
    @Async
    public void sendEmail(String to, String content) {
        // 异步发送邮件
    }
}

@RestController
public class AsyncController {
    @Autowired
    private AsyncService asyncService;
    
    @GetMapping("/async")
    public Result asyncTest() throws Exception {
        CompletableFuture<String> future = asyncService.processTask();
        // 可以继续处理其他事情
        String result = future.get(5, TimeUnit.SECONDS);
        return Result.success(result);
    }
}
```

---

**Q47：Spring Boot 中如何实现事件监听？**

**答：**

```java
// 1. 定义事件
public class UserRegisterEvent extends ApplicationEvent {
    private final User user;
    
    public UserRegisterEvent(Object source, User user) {
        super(source);
        this.user = user;
    }
    // getter
}

// 2. 发布事件
@Service
public class UserService {
    @Autowired
    private ApplicationEventPublisher publisher;
    
    @Transactional
    public User register(User user) {
        user = userRepository.save(user);
        // 发布事件
        publisher.publishEvent(new UserRegisterEvent(this, user));
        return user;
    }
}

// 3. 监听事件
@Component
public class UserRegisterListener {
    
    @EventListener
    @Async  // 异步处理
    public void handleUserRegister(UserRegisterEvent event) {
        User user = event.getUser();
        // 发送欢迎邮件
        // 初始化用户数据
        System.out.println("用户注册成功: " + user.getName());
    }
}

// 或者使用 @TransactionalEventListener
@Component
public class UserRegisterListener {
    
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleUserRegister(UserRegisterEvent event) {
        // 事务提交后才执行，确保数据已持久化
    }
}
```

---

**Q48：Spring Boot 如何处理跨域（CORS）问题？**

**答：**

**方式一：`@CrossOrigin` 注解**
```java
@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "http://example.com", maxAge = 3600)
public class UserController {
    // ...
}

// 方法级别
@GetMapping("/users")
@CrossOrigin(origins = {"http://example.com", "http://app.example.com"})
public List<User> list() {
    // ...
}
```

**方式二：全局配置**
```java
@Configuration
public class CorsConfig {
    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/api/**")
                    .allowedOrigins("http://example.com")
                    .allowedMethods("GET", "POST", "PUT", "DELETE")
                    .allowedHeaders("*")
                    .allowCredentials(true)
                    .maxAge(3600);
            }
        };
    }
}
```

**方式三：CorsFilter**
```java
@Configuration
public class CorsConfig {
    @Bean
    public CorsFilter corsFilter() {
        CorsConfiguration config = new CorsConfiguration();
        config.addAllowedOrigin("*");
        config.addAllowedMethod("*");
        config.addAllowedHeader("*");
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return new CorsFilter(source);
    }
}
```

---

**Q49：Spring Boot 如何实现国际化和多语言支持？**

**答：**

```java
// 配置
@Configuration
public class I18nConfig {
    @Bean
    public LocaleResolver localeResolver() {
        SessionLocaleResolver resolver = new SessionLocaleResolver();
        resolver.setDefaultLocale(Locale.SIMPLIFIED_CHINESE);
        return resolver;
    }
    
    @Bean
    public LocaleChangeInterceptor localeChangeInterceptor() {
        LocaleChangeInterceptor interceptor = new LocaleChangeInterceptor();
        interceptor.setParamName("lang");  // 通过 ?lang=en 切换语言
        return interceptor;
    }
    
    @Bean
    public WebMvcConfigurer webMvcConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addInterceptors(InterceptorRegistry registry) {
                registry.addInterceptor(localeChangeInterceptor());
            }
        };
    }
}
```

```properties
# messages.properties（默认）
welcome.message=欢迎使用系统
user.not.found=用户不存在

# messages_en.properties（英文）
welcome.message=Welcome to the system
user.not.found=User not found
```

```java
@RestController
public class I18nController {
    @Autowired
    private MessageSource messageSource;
    
    @GetMapping("/message")
    public Result getMessage(@RequestHeader(value = "Accept-Language", 
            defaultValue = "zh-CN") String lang) {
        Locale locale = Locale.forLanguageTag(lang);
        String message = messageSource.getMessage("welcome.message", null, locale);
        return Result.success(message);
    }
}
```

---

**Q50：Spring Boot 如何实现优雅停机？**

**答：**

```yaml
# application.yml
server:
  shutdown: graceful  # 优雅停机

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s  # 超时时间
```

```java
// 自定义优雅停机逻辑
@Component
public class GracefulShutdown {
    
    @PreDestroy
    public void onDestroy() {
        System.out.println("应用正在关闭，执行清理操作...");
        // 1. 停止接收新请求
        // 2. 等待处理中的请求完成
        // 3. 释放资源（数据库连接池、线程池等）
        // 4. 通知注册中心下线
    }
}
```

**通过 Actuator 关闭：**
```java
@RestController
public class ShutdownController {
    @Autowired
    private ApplicationContext context;
    
    @PostMapping("/shutdown")
    public String shutdown() {
        // 执行清理逻辑
        SpringApplication.exit(context, () -> 0);
        return "Shutting down...";
    }
}
```

---

**Q51：Spring Boot 3.x 有哪些重要变化？**

**答：**

| 变化 | Spring Boot 2.x | Spring Boot 3.x |
|-----|----------------|-----------------|
| **JDK 版本** | JDK 8+ | JDK 17+ |
| **Jakarta EE** | javax.* | jakarta.* |
| **自动配置** | spring.factories | AutoConfiguration.imports |
| **AOT 编译** | 不支持 | 支持 GraalVM Native |
| **虚拟线程** | 不支持 | 支持（JDK 21） |
| **Observability** | 无 | Micrometer 集成 |
| **HttpClient** | RestTemplate | HttpInterface |
| **问题诊断** | 无 | 问题报告（ProblemDetail） |

**迁移要点：**
```java
// 1. javax → jakarta
// import javax.servlet.*;        // 2.x
import jakarta.servlet.*;        // 3.x

// 2. HttpInterface（替代 RestTemplate）
@HttpExchange("/api/users")
public interface UserClient {
    @GetExchange("/{id}")
    User getUser(@PathVariable Long id);
}

// 3. 虚拟线程
@Bean
public TomcatProtocolHandlerCustomizer<?> protocolHandler() {
    return handler -> handler.setExecutor(Executors.newVirtualThreadPerTaskExecutor());
}
```

---

**Q52：Spring Boot 如何处理循环依赖？**

**答：**

**循环依赖示例：**
```java
@Service
public class AService {
    @Autowired
    private BService bService;
}

@Service
public class BService {
    @Autowired
    private AService aService;
}
```

**Spring 解决循环依赖的机制（三级缓存）：**
```text
singletonObjects（一级缓存）：完全创建好的 Bean
earlySingletonObjects（二级缓存）：早期暴露的 Bean（未完成属性填充）
singletonFactories（三级缓存）：Bean 工厂，可生成早期 Bean
```

**解决方案：**
```java
// 方式一：构造器注入 + @Lazy
@Service
public class AService {
    private final BService bService;
    
    public AService(@Lazy BService bService) {
        this.bService = bService;  // 延迟注入
    }
}

// 方式二：Setter 注入
@Service
public class AService {
    private BService bService;
    
    @Autowired
    public void setBService(BService bService) {
        this.bService = bService;
    }
}

// 方式三：重构设计（推荐）
// 提取公共逻辑到第三个类，消除循环依赖
@Service
public class CService {
    // 公共逻辑
}
```

---

**Q53：Spring Boot 中 Bean 的加载顺序如何控制？**

**答：**

```java
// 方式一：@DependsOn
@Configuration
public class AppConfig {
    
    @Bean
    @DependsOn("beanB")  // beanA 依赖 beanB，beanB 先创建
    public BeanA beanA() {
        return new BeanA();
    }
    
    @Bean
    public BeanB beanB() {
        return new BeanB();
    }
}

// 方式二：@Order + @AutoConfigureOrder
@Configuration
@AutoConfigureOrder(Ordered.HIGHEST_PRECEDENCE)  // 最高优先级
public class HighPriorityConfig {
    // 最先加载
}

// 方式三：实现接口
@Component
@Order(1)
public class FirstRunner implements CommandLineRunner {
    @Override
    public void run(String... args) {
        System.out.println("第一个执行");
    }
}

@Component
@Order(2)
public class SecondRunner implements CommandLineRunner {
    @Override
    public void run(String... args) {
        System.out.println("第二个执行");
    }
}
```

---

**Q54：Spring Boot 中如何使用 Profile 条件注入？**

**答：**

```java
// 方式一：@Profile 注解
@Configuration
public class ProfileConfig {
    
    @Bean
    @Profile("dev")
    public DataSource devDataSource() {
        return new HikariDataSource();  // 开发环境数据源
    }
    
    @Bean
    @Profile("prod")
    public DataSource prodDataSource() {
        return new HikariDataSource();  // 生产环境数据源
    }
}

// 方式二：配置文件
@Service
@Profile("!prod")  // 非生产环境生效
public class MockPaymentService implements PaymentService {
    // 模拟支付服务
}

@Service
@Profile("prod")   // 生产环境生效
public class RealPaymentService implements PaymentService {
    // 真实支付服务
}
```

```yaml
# 多环境激活
spring:
  profiles:
    active: dev
    # active: @spring.profiles.active@  # Maven 构建时替换
```

---

**Q55：Spring Boot 中常见的注解对比总结**

**答：**

| 对比 | 注解 1 | 注解 2 | 区别 |
|-----|--------|--------|------|
| 配置类 | `@Configuration` | `@Component` | Configuration 中 @Bean 方法默认单例 |
| 依赖注入 | `@Autowired` | `@Resource` | Autowired 按类型，Resource 按名称 |
| 请求映射 | `@RequestMapping` | `@GetMapping` | GetMapping 是特化版本 |
| 请求体 | `@RequestBody` | `@ModelAttribute` | RequestBody 处理 JSON，ModelAttribute 处理表单 |
| 路径变量 | `@PathVariable` | `@RequestParam` | PathVariable 从 URL 路径取，RequestParam 从查询参数取 |
| 事务 | `@Transactional` | `@EnableTransactionManagement` | Transactional 方法级，Enable 全局开关 |
| 组件扫描 | `@ComponentScan` | `@Import` | ComponentScan 扫描包，Import 导入类 |
| 条件装配 | `@ConditionalOnBean` | `@ConditionalOnMissingBean` | 一个要求存在，一个要求不存在 |
| 切面 | `@Aspect` | `@Around` | Aspect 定义切面，Around 定义通知 |
| 缓存 | `@Cacheable` | `@CacheEvict` | Cacheable 缓存结果，CacheEvict 清除缓存 |