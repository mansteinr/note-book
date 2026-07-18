# MyBatis 面试题汇总

> 适用版本：MyBatis 3.x | 适合 Java 开发人员面试准备及知识巩固

## 目录
- [一、MyBatis 基础概念](#一mybatis-基础概念)
- [二、核心配置](#二核心配置)
- [三、SQL 映射（XML & 注解）](#三sql-映射xml--注解)
- [四、动态 SQL](#四动态-sql)
- [五、缓存机制](#五缓存机制)
- [六、高级映射与关联查询](#六高级映射与关联查询)
- [七、插件与扩展](#七插件与扩展)
- [八、性能优化与最佳实践](#八性能优化与最佳实践)
- [九、MyBatis-Spring 整合](#九mybatis-spring-整合)

---

## 一、MyBatis 基础概念

**Q1：什么是 MyBatis？它的核心特性有哪些？**

**答：**
MyBatis 是一款优秀的**半自动持久层框架**，支持自定义 SQL、存储过程以及高级映射。它消除了几乎所有的 JDBC 代码和手动参数设置，使用简单的 XML 或注解进行配置和原始映射。

**核心特性：**

| 特性 | 说明 |
|-----|------|
| 半自动 ORM | 开发者需要手写 SQL，框架负责结果映射 |
| 动态 SQL | 基于 OGNL 表达式，灵活构建 SQL 语句 |
| 插件机制 | 支持拦截器扩展（Executor、ParameterHandler、ResultSetHandler、StatementHandler） |
| 缓存支持 | 内置一级缓存（SqlSession 级别）和二级缓存（Mapper 级别） |
| 映射灵活 | 支持 XML 配置和注解两种方式 |
| 数据库无关性 | 通过数据库方言（DatabaseIdProvider）适配不同数据库 |

**与 JPA/Hibernate 对比：**

| 对比维度 | MyBatis | Hibernate |
|---------|---------|-----------|
| SQL 控制 | 手写 SQL，完全可控 | 自动生成 SQL，HQL |
| 学习成本 | 较低 | 较高 |
| 性能优化 | 灵活，直接优化 SQL | 需深入理解 Hibernate 机制 |
| 适用场景 | 复杂查询、多表关联 | 标准 CRUD、对象关系复杂 |

```java
// MyBatis 核心工作流程
// 1. 加载配置文件
String resource = "mybatis-config.xml";
InputStream inputStream = Resources.getResourceAsStream(resource);
// 2. 创建 SqlSessionFactory
SqlSessionFactory sqlSessionFactory = new SqlSessionFactoryBuilder().build(inputStream);
// 3. 获取 SqlSession
try (SqlSession session = sqlSessionFactory.openSession()) {
    // 4. 执行 SQL
    User user = session.selectOne("com.example.UserMapper.selectById", 1);
}
```

---

**Q2：MyBatis 的 `#{}` 和 `${}` 有什么区别？**

**答：**
这是 MyBatis 面试中**最高频**的问题之一。

| 对比维度 | `#{}` | `${}` |
|---------|-------|-------|
| 处理方式 | 预编译占位符 `?` | 字符串直接拼接 |
| SQL 注入 | **安全**，防止 SQL 注入 | **不安全**，存在 SQL 注入风险 |
| 类型处理 | 自动添加引号（字符串） | 原样替换，不做类型处理 |
| 编译 | 预编译一次，可复用 | 每次都重新编译 |
| 使用场景 | 参数值（WHERE 条件、INSERT 值） | 表名、列名、ORDER BY 字段 |

```xml
<!-- #{} 安全写法：生成 SELECT * FROM user WHERE id = ? -->
<select id="selectById" resultType="User">
    SELECT * FROM user WHERE id = #{id}
</select>

<!-- ${} 特殊场景：按动态列名排序（需做好白名单校验） -->
<select id="selectByOrder" resultType="User">
    SELECT * FROM user ORDER BY ${orderColumn} ${sortDirection}
</select>
```

> ⚠️ **重要提醒**：能用 `#{}` 的地方绝不用 `${}`。若必须使用 `${}`，务必在业务层做好**白名单校验**。

---

**Q3：MyBatis 的工作原理是什么？**

**答：**
MyBatis 的工作流程可分为以下步骤：

```
配置文件加载 → SqlSessionFactory 构建 → SqlSession 创建 → Executor 执行 → SQL 解析映射 → 结果处理
```

**详细流程：**

1. **加载配置**：读取 `mybatis-config.xml`（全局配置）和 `Mapper.xml`（映射文件），解析为 `Configuration` 对象
2. **构建 SqlSessionFactory**：由 `SqlSessionFactoryBuilder` 根据 Configuration 创建
3. **获取 SqlSession**：从 SqlSessionFactory 的 `openSession()` 获取，每个线程应有自己的 SqlSession 实例
4. **获取 Mapper 代理**：通过 JDK 动态代理获取 Mapper 接口的代理对象
5. **执行 SQL**：代理对象调用 `Executor` 执行 SQL，经历 ParameterHandler 设置参数 → StatementHandler 执行 → ResultSetHandler 处理结果集
6. **事务管理**：执行完毕后提交或回滚，最后关闭 SqlSession

```java
// 核心组件调用链
// MapperProxy（JDK 动态代理）
//    → SqlSession（门面）
//      → Executor（执行器，含缓存逻辑）
//        → StatementHandler（SQL 语句处理器）
//          → ParameterHandler（参数处理器）
//          → ResultSetHandler（结果集处理器）
```

---

**Q4：MyBatis 的一级缓存和二级缓存有什么区别？**

**答：**

| 对比维度 | 一级缓存（Local Cache） | 二级缓存（Second Level Cache） |
|---------|------------------------|------------------------------|
| 作用范围 | SqlSession 级别 | Mapper 级别（namespace） |
| 是否默认开启 | **是**，默认开启 | **否**，需手动配置 |
| 生命周期 | 随 SqlSession 关闭而销毁 | 随应用生命周期（可配置过期时间） |
| 存储位置 | JVM 内存 | 可集成 Redis、Ehcache 等 |
| 数据共享 | 同一 SqlSession 内共享 | 多个 SqlSession 共享 |
| 失效条件 | 执行增删改 / 清空缓存 / 关闭 SqlSession | 执行增删改 / 配置过期时间 / 手动清空 |
| 线程安全 | 非线程安全 | 需注意缓存对象序列化 |

```xml
<!-- 二级缓存配置 -->
<cache eviction="LRU" flushInterval="60000" size="512" readOnly="true"/>

<!-- eviction: 回收策略（LRU | FIFO | SOFT | WEAK） -->
<!-- flushInterval: 刷新间隔（毫秒） -->
<!-- size: 缓存对象数量 -->
<!-- readOnly: 只读缓存（true则返回同一实例，性能好但需确保不改写） -->
```

```java
// 一级缓存示例
try (SqlSession session = sqlSessionFactory.openSession()) {
    UserMapper mapper = session.getMapper(UserMapper.class);
    User user1 = mapper.selectById(1);  // 查询数据库
    User user2 = mapper.selectById(1);  // 命中一级缓存，不查库
    System.out.println(user1 == user2); // true（同一对象）
}
```

> ⚠️ **注意**：一级缓存在与 Spring 整合时，每次查询默认创建新 SqlSession，一级缓存不生效。可通过事务管理让同一事务内复用 SqlSession。

---

**Q5：MyBatis 中 Mapper 接口的工作原理是什么？为什么 Mapper 接口没有实现类却能执行 SQL？**

**答：**
Mapper 接口通过 **JDK 动态代理** 实现，核心类是 `MapperProxy`。

**工作原理：**

1. `SqlSession.getMapper(Class)` 调用 `MapperRegistry.getMapper()`
2. 通过 `MapperProxyFactory` 创建 `MapperProxy` 代理对象
3. 调用接口方法时，被 `MapperProxy.invoke()` 拦截
4. 根据方法签名解析出 **namespace.id**（即 `接口全限定名.方法名`）
5. 调用 `SqlSession` 对应的方法（selectOne、selectList、insert、update、delete）

```java
// MapperProxy 核心逻辑（简化）
public class MapperProxy<T> implements InvocationHandler {
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) {
        // 如果是 Object 类方法，直接执行
        if (Object.class.equals(method.getDeclaringClass())) {
            return method.invoke(this, args);
        }
        // 构建 MapperMethod 并执行
        MapperMethod mapperMethod = cachedMapperMethod(method);
        return mapperMethod.execute(sqlSession, args);
    }
}
```

**关键约束：**
- Mapper 接口的**全限定名**必须与 XML 的 `namespace` 一致
- 方法名必须与 XML 中 SQL 语句的 `id` 一致
- 参数类型和返回类型必须与 XML 配置匹配

---

## 二、核心配置

**Q6：MyBatis 全局配置文件（mybatis-config.xml）中常用的配置项有哪些？**

**答：**

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE configuration PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-config.dtd">
<configuration>
    <!-- 1. 属性定义（支持外部配置文件引入） -->
    <properties resource="db.properties">
        <property name="username" value="root"/>
    </properties>

    <!-- 2. 全局设置 -->
    <settings>
        <setting name="cacheEnabled" value="true"/>         <!-- 全局缓存开关 -->
        <setting name="lazyLoadingEnabled" value="true"/>   <!-- 延迟加载 -->
        <setting name="mapUnderscoreToCamelCase" value="true"/> <!-- 驼峰转换 -->
        <setting name="logImpl" value="SLF4J"/>              <!-- 日志实现 -->
    </settings>

    <!-- 3. 类型别名 -->
    <typeAliases>
        <package name="com.example.entity"/>
    </typeAliases>

    <!-- 4. 插件 -->
    <plugins>
        <plugin interceptor="com.example.plugin.SqlLogPlugin"/>
    </plugins>

    <!-- 5. 环境配置（支持多环境） -->
    <environments default="development">
        <environment id="development">
            <transactionManager type="JDBC"/>
            <dataSource type="POOLED">
                <property name="driver" value="${db.driver}"/>
                <property name="url" value="${db.url}"/>
                <property name="username" value="${db.username}"/>
                <property name="password" value="${db.password}"/>
            </dataSource>
        </environment>
    </environments>

    <!-- 6. 数据库厂商标识 -->
    <databaseIdProvider type="DB_VENDOR">
        <property name="MySQL" value="mysql"/>
        <property name="Oracle" value="oracle"/>
    </databaseIdProvider>

    <!-- 7. Mapper 映射器注册 -->
    <mappers>
        <package name="com.example.mapper"/>
    </mappers>
</configuration>
```

**重要 settings 设置：**

| 设置项 | 默认值 | 说明 |
|-------|-------|------|
| `cacheEnabled` | true | 全局二级缓存开关 |
| `lazyLoadingEnabled` | false | 延迟加载全局开关 |
| `aggressiveLazyLoading` | false | 3.4.1+ 默认 false，按需加载 |
| `mapUnderscoreToCamelCase` | false | 下划线转驼峰（`user_name` → `userName`） |
| `useGeneratedKeys` | false | 是否使用 JDBC 的 getGeneratedKeys |
| `defaultExecutorType` | SIMPLE | 执行器类型（SIMPLE / REUSE / BATCH） |
| `logImpl` | 未设置 | 日志实现（SLF4J / LOG4J / STDOUT_LOGGING） |

---

**Q7：MyBatis 中 `<resultMap>` 的作用是什么？有哪些常用子元素？**

**答：**
`<resultMap>` 是 MyBatis 中最重要、最强大的元素之一，用于自定义查询结果与 Java 对象的映射关系。

**常用子元素：**

| 元素 | 作用 |
|------|------|
| `<id>` | 主键映射，提升性能（标记为 ID 有助于缓存） |
| `<result>` | 普通字段映射 |
| `<association>` | 一对一关联映射 |
| `<collection>` | 一对多关联映射 |
| `<discriminator>` | 鉴别器，根据某列值选择不同映射 |
| `<constructor>` | 构造方法注入 |

```xml
<resultMap id="userDetailMap" type="com.example.entity.User">
    <!-- 主键映射 -->
    <id property="id" column="user_id"/>
    <!-- 普通字段映射 -->
    <result property="userName" column="user_name"/>
    <result property="email" column="email"/>
    <!-- 一对一关联：用户 → 部门 -->
    <association property="department" javaType="com.example.entity.Department">
        <id property="id" column="dept_id"/>
        <result property="deptName" column="dept_name"/>
    </association>
    <!-- 一对多关联：用户 → 订单列表 -->
    <collection property="orders" ofType="com.example.entity.Order">
        <id property="orderId" column="order_id"/>
        <result property="amount" column="amount"/>
        <result property="createTime" column="order_create_time"/>
    </collection>
</resultMap>

<select id="selectUserDetail" resultMap="userDetailMap">
    SELECT u.id AS user_id, u.user_name, u.email,
           d.id AS dept_id, d.name AS dept_name,
           o.id AS order_id, o.amount, o.create_time AS order_create_time
    FROM user u
    LEFT JOIN department d ON u.dept_id = d.id
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.id = #{id}
</select>
```

> 💡 **最佳实践**：复杂查询优先使用 `<resultMap>` 而非直接用 `resultType`，这样既清晰又可复用。

---

**Q8：MyBatis 中 XML 映射和注解映射各有什么优缺点？如何选择？**

**答：**

| 对比维度 | XML 映射 | 注解映射 |
|---------|---------|---------|
| SQL 可读性 | 复杂 SQL 表达清晰 | 复杂 SQL 可读性差 |
| 动态 SQL | **完整支持**（`<if>`、`<foreach>` 等） | 需 `@SelectProvider` 或脚本方式，较弱 |
| 结果映射 | 功能强大，支持继承 | 简单场景可用，复杂映射困难 |
| 维护性 | SQL 与 Java 代码分离 | SQL 与接口耦合 |
| 适用场景 | 复杂查询、企业级项目 | 简单 CRUD、快速开发 |

```java
// 注解方式示例
@Mapper
public interface UserMapper {
    @Select("SELECT * FROM user WHERE id = #{id}")
    User selectById(Long id);

    @Insert("INSERT INTO user(user_name, email) VALUES(#{userName}, #{email})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(User user);

    // 复杂 SQL 使用 @SelectProvider
    @SelectProvider(type = UserSqlProvider.class, method = "selectByCondition")
    List<User> selectByCondition(UserQuery query);
}
```

> 💡 **最佳实践**：**XML 优先**用于复杂业务，注解用于简单 CRUD。实际项目中两者可混合使用（同个 Mapper 接口）。

---

## 三、SQL 映射（XML & 注解）

**Q9：MyBatis 如何获取自增主键？**

**答：**
MyBatis 提供了两种方式获取插入后的自增主键：

**方式一：`useGeneratedKeys`（推荐，支持 JDBC 3.0+ 的数据库）**

```xml
<!-- XML 方式 -->
<insert id="insert" parameterType="User" useGeneratedKeys="true" keyProperty="id">
    INSERT INTO user(user_name, email) VALUES(#{userName}, #{email})
</insert>
```

```java
// 注解方式
@Insert("INSERT INTO user(user_name, email) VALUES(#{userName}, #{email})")
@Options(useGeneratedKeys = true, keyProperty = "id")
int insert(User user);

// 调用后，user.getId() 即为自增主键值
```

**方式二：`<selectKey>`（适用于不支持自动生成主键的数据库，如 Oracle）**

```xml
<insert id="insert" parameterType="User">
    <!-- Oracle 序列方式 -->
    <selectKey keyProperty="id" resultType="long" order="BEFORE">
        SELECT seq_user.nextval FROM DUAL
    </selectKey>
    INSERT INTO user(id, user_name, email) VALUES(#{id}, #{userName}, #{email})
</insert>
```

| 属性 | 说明 |
|------|------|
| `keyProperty` | 主键对应的 Java 对象属性名 |
| `keyColumn` | 主键列名（可选，与 keyProperty 不同时使用） |
| `order` | BEFORE（插入前获取） / AFTER（插入后获取） |
| `resultType` | 主键的 Java 类型 |

---

**Q10：MyBatis 如何传递多个参数？**

**答：**
MyBatis 支持多种参数传递方式：

**方式一：使用 `@Param` 注解（推荐）**

```java
// 接口定义
User selectByCondition(@Param("userName") String userName, @Param("email") String email);

// XML 中直接使用参数名
<select id="selectByCondition" resultType="User">
    SELECT * FROM user WHERE user_name = #{userName} AND email = #{email}
</select>
```

**方式二：使用 JavaBean 封装**

```java
// 查询对象
public class UserQuery {
    private String userName;
    private String email;
    // getter/setter...
}

// 接口
List<User> selectByQuery(UserQuery query);

// XML
<select id="selectByQuery" resultType="User">
    SELECT * FROM user
    WHERE user_name = #{userName} AND email = #{email}
</select>
```

**方式三：使用 Map**

```java
Map<String, Object> params = new HashMap<>();
params.put("userName", "张三");
params.put("email", "zhangsan@example.com");
List<User> users = mapper.selectByMap(params);
```

**方式四：默认顺序参数（不推荐）**

```java
// 无 @Param 时，使用 arg0, arg1 / param1, param2
<select id="selectByCondition" resultType="User">
    SELECT * FROM user WHERE user_name = #{arg0} AND email = #{arg1}
    <!-- 或者 -->
    SELECT * FROM user WHERE user_name = #{param1} AND email = #{param2}
</select>
```

> 💡 **最佳实践**：参数超过 1 个时，始终使用 `@Param` 明确指定参数名，提高代码可读性。

---

**Q11：MyBatis 中模糊查询有几种写法？**

**答：**

```java
// 方式一：Java 代码拼接 %（推荐，安全）
String userName = "%" + keyword + "%";
List<User> users = mapper.selectByLikeName(userName);

// XML
<select id="selectByLikeName" resultType="User">
    SELECT * FROM user WHERE user_name LIKE #{userName}
</select>
```

```xml
<!-- 方式二：SQL 中使用 CONCAT 函数 -->
<select id="selectByLikeName2" resultType="User">
    SELECT * FROM user WHERE user_name LIKE CONCAT('%', #{keyword}, '%')
</select>
```

```xml
<!-- 方式三：使用 bind 标签 -->
<select id="selectByLikeName3" resultType="User">
    <bind name="pattern" value="'%' + keyword + '%'"/>
    SELECT * FROM user WHERE user_name LIKE #{pattern}
</select>
```

```xml
<!-- 方式四：${} 拼接（不安全，不推荐） -->
<select id="selectByLikeName4" resultType="User">
    SELECT * FROM user WHERE user_name LIKE '%${keyword}%'
</select>
```

> ⚠️ **注意**：方式四存在 SQL 注入风险，不推荐在生产环境使用。优先使用方式一或方式二。

---

**Q12：MyBatis 如何处理枚举类型映射？**

**答：**

```java
// 枚举定义
public enum Gender {
    MALE(1, "男"),
    FEMALE(2, "女");

    private final int code;
    private final String desc;
    // getter...
}

public class User {
    private Gender gender;
    // ...
}
```

**方式一：`EnumTypeHandler`（默认，存储枚举名称）**

存储到数据库的是 `MALE` / `FEMALE`（字符串）。

**方式二：`EnumOrdinalTypeHandler`（存储枚举序号）**

存储到数据库的是 `0` / `1`（整数）。

**方式三：自定义 TypeHandler（推荐）**

```java
// 自定义枚举类型处理器
public class GenderTypeHandler extends BaseTypeHandler<Gender> {
    @Override
    public void setNonNullParameter(PreparedStatement ps, int i, Gender parameter, JdbcType jdbcType) throws SQLException {
        ps.setInt(i, parameter.getCode());  // 存储 code 值
    }

    @Override
    public Gender getNullableResult(ResultSet rs, String columnName) throws SQLException {
        int code = rs.getInt(columnName);
        return Gender.fromCode(code);  // 根据 code 获取枚举
    }

    @Override
    public Gender getNullableResult(ResultSet rs, int columnIndex) throws SQLException {
        int code = rs.getInt(columnIndex);
        return Gender.fromCode(code);
    }

    @Override
    public Gender getNullableResult(CallableStatement cs, int columnIndex) throws SQLException {
        int code = cs.getInt(columnIndex);
        return Gender.fromCode(code);
    }
}
```

```xml
<!-- 在映射文件中指定 -->
<result column="gender" property="gender" typeHandler="com.example.handler.GenderTypeHandler"/>
```

---

## 四、动态 SQL

**Q13：MyBatis 动态 SQL 有哪些常用标签？**

**答：**

| 标签 | 作用 | 示例 |
|------|------|------|
| `<if>` | 条件判断 | `<if test="name != null and name != ''">` |
| `<choose> / <when> / <otherwise>` | 多条件选择（类似 switch） | 选择第一个满足的 when |
| `<where>` | 自动添加 WHERE 并处理 AND/OR 前缀 | 包裹条件语句 |
| `<set>` | 自动添加 SET 并处理逗号后缀 | 用于 UPDATE 语句 |
| `<foreach>` | 遍历集合 | 用于 IN 查询、批量插入 |
| `<trim>` | 自定义字符串截取 | 更灵活的 where/set 替代 |
| `<bind>` | 创建变量并绑定到上下文 | 模糊查询拼接 OGNL 表达式 |
| `<sql> / <include>` | SQL 片段复用 | 提取公共 SQL 片段 |

```xml
<!-- 动态查询示例 -->
<select id="selectByCondition" resultType="User">
    SELECT * FROM user
    <where>
        <if test="userName != null and userName != ''">
            AND user_name = #{userName}
        </if>
        <if test="email != null and email != ''">
            AND email = #{email}
        </if>
        <if test="status != null">
            AND status = #{status}
        </if>
        <if test="idList != null and idList.size() > 0">
            AND id IN
            <foreach collection="idList" item="id" open="(" separator="," close=")">
                #{id}
            </foreach>
        </if>
    </where>
    <if test="orderBy != null">
        ORDER BY ${orderBy}
    </if>
</select>
```

---

**Q14：`<where>` 和 `<trim>` 的区别是什么？**

**答：**
`<where>` 是 `<trim>` 的特定场景封装，等价于：

```xml
<trim prefix="WHERE" prefixOverrides="AND |OR ">
    <!-- 条件 -->
</trim>
```

而 `<set>` 等价于：

```xml
<trim prefix="SET" suffixOverrides=",">
    <!-- 更新字段 -->
</trim>
```

```xml
<!-- 使用 <trim> 实现更灵活的动态 UPDATE -->
<update id="updateSelective">
    UPDATE user
    <trim prefix="SET" suffixOverrides=",">
        <if test="userName != null">user_name = #{userName},</if>
        <if test="email != null">email = #{email},</if>
        <if test="status != null">status = #{status},</if>
    </trim>
    WHERE id = #{id}
</update>
```

> 💡 **最佳实践**：日常开发中 `<where>` 和 `<set>` 够用，`<trim>` 用于更复杂的场景（如自定义前缀后缀处理）。

---

**Q15：`<foreach>` 标签的详细用法及批量操作示例？**

**答：**

```xml
<!-- 批量查询（IN 查询） -->
<select id="selectByIds" resultType="User">
    SELECT * FROM user WHERE id IN
    <foreach collection="ids" item="id" open="(" separator="," close=")">
        #{id}
    </foreach>
</select>
```

```xml
<!-- 批量插入（方式一：多条 INSERT 语句） -->
<insert id="batchInsert">
    INSERT INTO user(user_name, email, status) VALUES
    <foreach collection="list" item="user" separator=",">
        (#{user.userName}, #{user.email}, #{user.status})
    </foreach>
</insert>
```

```xml
<!-- 批量插入（方式二：配合 ExecutorType.BATCH） -->
<insert id="insert">
    INSERT INTO user(user_name, email, status) VALUES(#{userName}, #{email}, #{status})
</insert>
```

```java
// 方式二 Java 调用（BATCH 模式，推荐大数据量时使用）
try (SqlSession session = sqlSessionFactory.openSession(ExecutorType.BATCH)) {
    UserMapper mapper = session.getMapper(UserMapper.class);
    for (User user : userList) {
        mapper.insert(user);
    }
    session.commit();
}
```

```xml
<!-- 批量更新（MySQL CASE WHEN 方式） -->
<update id="batchUpdate">
    <foreach collection="list" item="user" separator=";">
        UPDATE user
        SET user_name = #{user.userName}, email = #{user.email}
        WHERE id = #{user.id}
    </foreach>
</update>
```

**`<foreach>` 属性说明：**

| 属性 | 说明 |
|------|------|
| `collection` | 集合参数名（list / array / @Param 指定的名称） |
| `item` | 当前迭代元素 |
| `index` | 当前迭代索引 |
| `open` | 开始符号 |
| `separator` | 分隔符 |
| `close` | 结束符号 |

> ⚠️ **注意**：MySQL 批量更新需在 JDBC 连接 URL 中添加 `&allowMultiQueries=true`。

---

**Q16：动态 SQL 中 `<if test="">` 的判断规则是什么？**

**答：**
`<if>` 标签的 `test` 属性使用 **OGNL 表达式**，常见判断规则如下：

```xml
<!-- 字符串非空判断 -->
<if test="userName != null and userName != ''">
    AND user_name = #{userName}
</if>

<!-- 数值比较 -->
<if test="age > 18">
    AND age > #{age}
</if>

<!-- 集合判断 -->
<if test="idList != null and idList.size() > 0">
    AND id IN <foreach .../>
</if>

<!-- 枚举比较 -->
<if test="status == @com.example.enums.Status@ACTIVE">
    AND status = #{status}
</if>

<!-- 字符串 equals 判断 -->
<if test="gender == 'MALE'.toString()">
    AND gender = #{gender}
</if>

<!-- 布尔值判断 -->
<if test="isDeleted">
    AND is_deleted = 1
</if>
```

> ⚠️ **常见坑**：`<if test="userName != null and userName != ''">` 中，如果 `userName` 是数字类型，`userName != ''` 永远为 true，可能导致意外行为。建议数字类型只判断 null。

---

## 五、缓存机制

**Q17：MyBatis 二级缓存如何配置和使用？使用时需要注意什么？**

**答：**

**配置步骤：**

```xml
<!-- 1. 全局配置开启二级缓存（默认 true，可不配置） -->
<settings>
    <setting name="cacheEnabled" value="true"/>
</settings>

<!-- 2. Mapper 文件中添加 <cache/> 标签 -->
<mapper namespace="com.example.mapper.UserMapper">
    <!-- 基础配置 -->
    <cache eviction="LRU" flushInterval="60000" size="512" readOnly="false"/>

    <!-- 集成第三方缓存（如 Redis） -->
    <!-- <cache type="org.mybatis.caches.redis.RedisCache"/> -->

    <select id="selectById" resultType="User" useCache="true">
        SELECT * FROM user WHERE id = #{id}
    </select>
</mapper>
```

**3. 实体类必须实现 Serializable**

```java
public class User implements Serializable {
    private static final long serialVersionUID = 1L;
    // ...
}
```

**注意事项：**

| 注意点 | 说明 |
|-------|------|
| 序列化 | 缓存对象必须实现 `Serializable` |
| 事务 | 增删改操作会清空当前 namespace 的二级缓存 |
| 脏读风险 | 多表关联查询中，关联表更新不会触发缓存清理 |
| 缓存粒度 | 建议按 namespace 细化缓存配置 |
| 分布式环境 | 本地缓存不适用，需集成 Redis 等分布式缓存 |

```xml
<!-- 使用 <cache-ref> 引用其他 namespace 的缓存 -->
<cache-ref namespace="com.example.mapper.UserMapper"/>
```

---

**Q18：MyBatis 一级缓存失效的场景有哪些？**

**答：**
一级缓存（SqlSession 级别）在以下场景会失效：

```java
// 场景一：不同 SqlSession
try (SqlSession session1 = sqlSessionFactory.openSession();
     SqlSession session2 = sqlSessionFactory.openSession()) {
    UserMapper mapper1 = session1.getMapper(UserMapper.class);
    UserMapper mapper2 = session2.getMapper(UserMapper.class);
    mapper1.selectById(1);  // 查询数据库
    mapper2.selectById(1);  // 再次查询数据库（不同 SqlSession）
}
```

```java
// 场景二：同一 SqlSession 中执行了增删改操作
try (SqlSession session = sqlSessionFactory.openSession()) {
    UserMapper mapper = session.getMapper(UserMapper.class);
    mapper.selectById(1);  // 查询数据库，放入一级缓存
    mapper.insert(new User(...));  // 增删改会清空一级缓存
    mapper.selectById(1);  // 再次查询数据库
}
```

```java
// 场景三：手动清空缓存
session.clearCache();
```

```java
// 场景四：与 Spring 整合时（默认每次查询使用新 SqlSession）
// 需要开启事务才能让同一事务内复用 SqlSession
@Service
@Transactional  // 开启事务，同一事务内共享 SqlSession
public class UserService {
    public void test() {
        userMapper.selectById(1);  // 查库
        userMapper.selectById(1);  // 命中一级缓存
    }
}
```

---

## 六、高级映射与关联查询

**Q19：MyBatis 中延迟加载（懒加载）如何配置？原理是什么？**

**答：**

**配置方式：**

```xml
<!-- 全局配置 -->
<settings>
    <!-- 开启延迟加载（3.4.1+ 默认 false） -->
    <setting name="lazyLoadingEnabled" value="true"/>
    <!-- 按需加载（3.4.1+ 默认 false，false 表示按需加载） -->
    <setting name="aggressiveLazyLoading" value="false"/>
</settings>
```

```xml
<!-- 局部配置：指定关联查询的加载方式 -->
<association property="department" javaType="Department"
             select="selectDepartmentById" column="dept_id"
             fetchType="lazy"/>  <!-- lazy | eager -->
```

```java
// 使用示例
User user = userMapper.selectById(1);
System.out.println(user.getUserName());  // 此时尚未加载 department
Department dept = user.getDepartment();  // 首次访问时触发加载
System.out.println(dept.getDeptName());  // 数据已加载
```

**原理：**
MyBatis 使用 **CGLIB 或 Javassist** 创建代理对象。当访问关联属性时，代理对象拦截调用并触发额外的 SQL 查询。

```java
// 延迟加载流程
// 1. User 对象实际是代理对象
// 2. 调用 user.getDepartment() 时触发代理拦截
// 3. 代理执行 selectDepartmentById 查询
// 4. 将查询结果设置到 User 对象
// 5. 返回 department 对象
```

> ⚠️ **注意**：延迟加载需要在同一个 SqlSession 生命周期内完成。与 Spring 整合时，若 Service 层未开启事务，延迟加载可能因 SqlSession 已关闭而失败（经典的 `LazyInitializationException`）。

---

**Q20：`<association>` 关联查询的两种方式（嵌套查询 vs 嵌套结果）？**

**答：**

**方式一：嵌套查询（N+1 问题）**

```xml
<resultMap id="userMap" type="User">
    <id property="id" column="id"/>
    <result property="userName" column="user_name"/>
    <!-- 通过 select 属性指定额外查询 -->
    <association property="department" javaType="Department"
                 column="dept_id" select="selectDepartmentById"/>
</resultMap>

<select id="selectById" resultMap="userMap">
    SELECT * FROM user WHERE id = #{id}
</select>

<select id="selectDepartmentById" resultType="Department">
    SELECT * FROM department WHERE id = #{dept_id}
</select>
```

**方式二：嵌套结果（推荐，单次 JOIN 查询）**

```xml
<resultMap id="userMap" type="User">
    <id property="id" column="id"/>
    <result property="userName" column="user_name"/>
    <!-- 直接在 resultMap 中定义映射 -->
    <association property="department" javaType="Department">
        <id property="id" column="dept_id"/>
        <result property="deptName" column="dept_name"/>
    </association>
</resultMap>

<select id="selectById" resultMap="userMap">
    SELECT u.id, u.user_name, d.id AS dept_id, d.name AS dept_name
    FROM user u LEFT JOIN department d ON u.dept_id = d.id
    WHERE u.id = #{id}
</select>
```

| 对比 | 嵌套查询（select） | 嵌套结果（resultMap） |
|------|-------------------|----------------------|
| SQL 次数 | 1 + N 次 | 1 次 |
| 性能 | 差（N+1 问题） | 好 |
| 延迟加载 | 天然支持 | 需配合 lazyLoadingEnabled |
| 灵活性 | 高（可复用已有查询） | 低（需单独写 JOIN） |

> 💡 **最佳实践**：优先使用嵌套结果方式，避免 N+1 问题。仅在需要延迟加载且数据量小时使用嵌套查询。

---

**Q21：MyBatis 如何处理一对多和多对多映射？**

**答：**

```xml
<!-- 一对多映射：用户 → 订单列表 -->
<resultMap id="userWithOrdersMap" type="User">
    <id property="id" column="user_id"/>
    <result property="userName" column="user_name"/>
    <collection property="orders" ofType="Order">
        <id property="orderId" column="order_id"/>
        <result property="amount" column="amount"/>
        <result property="createTime" column="create_time"/>
    </collection>
</resultMap>

<select id="selectUserWithOrders" resultMap="userWithOrdersMap">
    SELECT u.id AS user_id, u.user_name,
           o.id AS order_id, o.amount, o.create_time
    FROM user u LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.id = #{id}
</select>
```

```xml
<!-- 多对多映射：学生 → 课程列表（通过中间表 student_course） -->
<resultMap id="studentWithCoursesMap" type="Student">
    <id property="id" column="student_id"/>
    <result property="name" column="student_name"/>
    <collection property="courses" ofType="Course">
        <id property="id" column="course_id"/>
        <result property="courseName" column="course_name"/>
        <result property="score" column="score"/>
    </collection>
</resultMap>

<select id="selectStudentWithCourses" resultMap="studentWithCoursesMap">
    SELECT s.id AS student_id, s.name AS student_name,
           c.id AS course_id, c.name AS course_name, sc.score
    FROM student s
    LEFT JOIN student_course sc ON s.id = sc.student_id
    LEFT JOIN course c ON sc.course_id = c.id
    WHERE s.id = #{id}
</select>
```

**`<collection>` 关键属性：**

| 属性 | 说明 |
|------|------|
| `property` | 集合属性名 |
| `ofType` | 集合中元素的类型 |
| `column` | 关联列（嵌套查询时使用） |
| `select` | 嵌套查询的 statement id |
| `fetchType` | 加载方式（lazy / eager） |

---

**Q22：`<discriminator>` 鉴别器的使用场景是什么？**

**答：**
鉴别器类似 Java 的 `switch` 语句，根据某列的值选择不同的映射规则。

```xml
<!-- 场景：不同类型的车辆有不同的属性 -->
<resultMap id="vehicleMap" type="Vehicle">
    <id property="id" column="id"/>
    <result property="brand" column="brand"/>
    <result property="price" column="price"/>
    <discriminator javaType="string" column="vehicle_type">
        <!-- 汽车 -->
        <case value="CAR" resultType="Car">
            <result property="seatCount" column="seat_count"/>
            <result property="fuelType" column="fuel_type"/>
        </case>
        <!-- 卡车 -->
        <case value="TRUCK" resultType="Truck">
            <result property="loadCapacity" column="load_capacity"/>
            <result property="axleCount" column="axle_count"/>
        </case>
    </discriminator>
</resultMap>
```

```java
// 实体类设计
public class Vehicle {
    private Long id;
    private String brand;
    private BigDecimal price;
    private String vehicleType;
}

public class Car extends Vehicle {
    private Integer seatCount;
    private String fuelType;
}

public class Truck extends Vehicle {
    private BigDecimal loadCapacity;
    private Integer axleCount;
}
```

---

## 七、插件与扩展

**Q23：MyBatis 插件机制的原理是什么？如何自定义插件？**

**答：**
MyBatis 插件基于 **责任链模式 + JDK 动态代理** 实现，允许拦截以下四个核心对象的方法：

| 拦截对象 | 可拦截方法 |
|---------|-----------|
| `Executor` | update、query、flushStatements、commit、rollback、getTransaction、close、isClosed |
| `ParameterHandler` | getParameterObject、setParameters |
| `ResultSetHandler` | handleResultSets、handleOutputParameters |
| `StatementHandler` | prepare、parameterize、batch、update、query |

```java
// 自定义 SQL 日志插件
@Intercepts({
    @Signature(type = StatementHandler.class,
               method = "prepare",
               args = {Connection.class, Integer.class})
})
public class SqlLogPlugin implements Interceptor {
    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        // 获取 StatementHandler
        StatementHandler handler = (StatementHandler) invocation.getTarget();
        // 获取绑定的 SQL
        BoundSql boundSql = handler.getBoundSql();
        String sql = boundSql.getSql().replaceAll("\\s+", " ");
        long start = System.currentTimeMillis();
        try {
            // 执行原方法
            return invocation.proceed();
        } finally {
            long cost = System.currentTimeMillis() - start;
            System.out.println("SQL: " + sql + " | Cost: " + cost + "ms");
        }
    }

    @Override
    public Object plugin(Object target) {
        // 使用 Plugin.wrap 创建代理
        return Plugin.wrap(target, this);
    }

    @Override
    public void setProperties(Properties properties) {
        // 读取插件配置属性
    }
}
```

```xml
<!-- 注册插件 -->
<plugins>
    <plugin interceptor="com.example.plugin.SqlLogPlugin">
        <property name="slowSqlThreshold" value="1000"/>
    </plugin>
</plugins>
```

**执行流程：**

```
Executor → StatementHandler → ParameterHandler → ResultSetHandler
    ↑            ↑                  ↑                  ↑
    └── 插件代理链 ──────┘
```

> ⚠️ **注意**：多个插件按配置顺序形成代理链，每个插件都会对目标对象进行一层代理包装。插件过多会影响性能。

---

**Q24：MyBatis 分页插件（PageHelper）的原理是什么？**

**答：**
PageHelper 是 MyBatis 最常用的分页插件，基于 MyBatis 的插件机制实现。

**原理：**

1. 拦截 `Executor.query()` 方法
2. 在 SQL 执行前，通过 `ThreadLocal` 获取分页参数
3. 根据数据库方言，对原始 SQL 进行包装，生成分页 SQL
4. 执行分页 SQL 获取数据
5. 执行 COUNT SQL 获取总数
6. 将结果封装为 `Page` 对象

```java
// 使用示例
// 在查询前调用 startPage
PageHelper.startPage(1, 10);
List<User> users = userMapper.selectByCondition(query);
PageInfo<User> pageInfo = new PageInfo<>(users);
// pageInfo.getTotal()   // 总记录数
// pageInfo.getPages()   // 总页数
```

**核心拦截器逻辑（简化）：**

```java
@Intercepts(@Signature(type = Executor.class, method = "query",
    args = {MappedStatement.class, Object.class, RowBounds.class, ResultHandler.class}))
public class PageInterceptor implements Interceptor {
    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        // 1. 从 ThreadLocal 获取分页参数
        Page page = PageHelper.getLocalPage();
        if (page == null) {
            return invocation.proceed();
        }
        // 2. 执行 COUNT 查询获取总数
        Long total = executeCountQuery(invocation);
        page.setTotal(total);
        // 3. 包装分页 SQL 并执行
        String pageSql = dialect.getPageSql(originalSql, page);
        return executePageQuery(invocation, pageSql, page);
    }
}
```

---

**Q25：MyBatis-Plus 与原生 MyBatis 有什么区别？**

**答：**

| 对比维度 | MyBatis | MyBatis-Plus |
|---------|---------|-------------|
| 基础 CRUD | 需手写 SQL 或简单注解 | **内置通用 Mapper**，开箱即用 |
| 条件构造器 | 无 | `QueryWrapper`、`UpdateWrapper` |
| 分页插件 | 需第三方（PageHelper） | **内置分页插件** |
| 代码生成器 | 无 | **内置代码生成器** |
| 乐观锁 | 手动实现 | 注解 + 插件自动处理 |
| 逻辑删除 | 手动实现 | 注解 `@TableLogic` |
| 自动填充 | 手动实现 | `@TableField(fill = ...)` |
| 多租户 | 插件实现 | 内置多租户插件 |

```java
// MyBatis-Plus 示例
@Mapper
public interface UserMapper extends BaseMapper<User> {
    // 继承 BaseMapper 后，自动拥有 CRUD 方法
    // insert、deleteById、updateById、selectById、selectList 等
}

// 使用条件构造器
List<User> users = userMapper.selectList(
    new QueryWrapper<User>()
        .eq("status", 1)
        .like("user_name", "张")
        .orderByDesc("create_time")
        .last("LIMIT 10")
);
```

> 💡 **选择建议**：新项目推荐使用 MyBatis-Plus，减少重复代码。传统项目或对 SQL 有严格要求时使用原生 MyBatis。

---

## 八、性能优化与最佳实践

**Q26：MyBatis 有哪些性能优化手段？**

**答：**

**1. SQL 层面优化**

```java
// 批量操作使用 BATCH 模式
try (SqlSession session = sqlSessionFactory.openSession(ExecutorType.BATCH)) {
    UserMapper mapper = session.getMapper(UserMapper.class);
    for (User user : userList) {
        mapper.insert(user);
    }
    session.commit();  // 一次性提交
}
```

**2. 配置优化**

```xml
<settings>
    <!-- 开启驼峰转换，减少别名书写 -->
    <setting name="mapUnderscoreToCamelCase" value="true"/>
    <!-- 复用预编译的 SQL 语句 -->
    <setting name="defaultExecutorType" value="REUSE"/>
    <!-- 开启懒加载，减少不必要查询 -->
    <setting name="lazyLoadingEnabled" value="true"/>
    <setting name="aggressiveLazyLoading" value="false"/>
    <!-- 设置默认的 fetchSize -->
    <setting name="defaultFetchSize" value="100"/>
</settings>
```

**3. 避免 N+1 查询**

```xml
<!-- 错误：嵌套查询导致 N+1 -->
<collection property="orders" column="id"
            select="selectOrdersByUserId"/>  <!-- 每个用户额外N次查询 -->

<!-- 正确：关联查询一次完成 -->
<collection property="orders" ofType="Order">
    <id property="id" column="order_id"/>
</collection>
```

**4. 大数据量导出优化**

```java
// 使用流式查询（Cursor），避免 OOM
try (SqlSession session = sqlSessionFactory.openSession();
     Cursor<User> cursor = session.selectCursor("selectAll")) {
    cursor.forEach(user -> {
        // 逐条处理，不占用大量内存
        processUser(user);
    });
}
```

**5. 其他优化手段**

| 优化项 | 说明 |
|-------|------|
| 合理使用二级缓存 | 对读多写少的表开启二级缓存 |
| 连接池调优 | 调整 Druid/HikariCP 连接池参数 |
| 避免 `SELECT *` | 只查询需要的列 |
| 使用 `<sql>` 复用 | 提取公共 SQL 片段 |
| 索引优化 | 确保 WHERE/ORDER BY 列有索引 |
| 分页查询优化 | 使用游标分页替代 OFFSET 分页 |

---

**Q27：MyBatis 中如何避免 SQL 注入？**

**答：**

**原则：始终使用 `#{}` 代替 `${}`。**

```xml
<!-- ✅ 安全：使用 #{} -->
<select id="selectById" resultType="User">
    SELECT * FROM user WHERE id = #{id}
</select>

<!-- ❌ 危险：使用 ${} -->
<select id="selectById" resultType="User">
    SELECT * FROM user WHERE id = ${id}
</select>
```

**必须使用 `${}` 时的安全措施：**

```java
// 场景：动态排序字段
// 1. 定义白名单
private static final Set<String> ALLOWED_COLUMNS = Set.of("id", "user_name", "email", "create_time");
private static final Set<String> ALLOWED_DIRECTIONS = Set.of("ASC", "DESC");

// 2. 业务层校验
public List<User> selectByOrder(String orderColumn, String sortDirection) {
    if (orderColumn == null || !ALLOWED_COLUMNS.contains(orderColumn)) {
        throw new IllegalArgumentException("Invalid column: " + orderColumn);
    }
    if (sortDirection == null || !ALLOWED_DIRECTIONS.contains(sortDirection.toUpperCase())) {
        throw new IllegalArgumentException("Invalid direction: " + sortDirection);
    }
    return mapper.selectByOrder(orderColumn, sortDirection.toUpperCase());
}
```

```xml
<!-- 通过白名单校验后使用 ${} -->
<select id="selectByOrder" resultType="User">
    SELECT * FROM user ORDER BY ${orderColumn} ${sortDirection}
</select>
```

---

**Q28：MyBatis 事务管理机制是怎样的？**

**答：**
MyBatis 提供了两种事务管理器：

**1. JDBC 事务管理器**

```xml
<environment id="development">
    <transactionManager type="JDBC"/>
    <dataSource type="POOLED">...</dataSource>
</environment>
```

```java
// 手动管理事务
try (SqlSession session = sqlSessionFactory.openSession()) {
    UserMapper mapper = session.getMapper(UserMapper.class);
    mapper.insert(user1);
    mapper.insert(user2);
    session.commit();  // 手动提交
} catch (Exception e) {
    session.rollback();  // 手动回滚
}
```

**2. MANAGED 事务管理器（容器管理）**

```xml
<environment id="production">
    <transactionManager type="MANAGED"/>
    <dataSource type="JNDI">...</dataSource>
</environment>
```

**与 Spring 整合时的事务管理：**

```java
// Spring 管理事务，MyBatis 的 SqlSession 生命周期由 Spring 控制
@Service
@Transactional  // 由 Spring 事务管理器接管
public class UserService {
    @Autowired
    private UserMapper userMapper;

    @Autowired
    private OrderMapper orderMapper;

    public void createUserWithOrder(User user, Order order) {
        userMapper.insert(user);      // 同一事务
        order.setUserId(user.getId());
        orderMapper.insert(order);    // 同一事务
        // 方法正常结束 → 提交事务
        // 抛出 RuntimeException → 回滚事务
    }
}
```

**事务传播行为：**

```java
@Transactional(propagation = Propagation.REQUIRED)          // 默认：有则加入，无则创建
@Transactional(propagation = Propagation.REQUIRES_NEW)      // 新建事务，挂起当前事务
@Transactional(propagation = Propagation.NESTED)            // 嵌套事务（savepoint）
@Transactional(propagation = Propagation.SUPPORTS)          // 有则加入，无则非事务执行
```

---

**Q29：MyBatis 如何处理大字段（CLOB / BLOB）？**

**答：**

```java
// 实体类定义
public class Document {
    private Long id;
    private String title;
    private String content;    // CLOB：大文本
    private byte[] attachment;  // BLOB：二进制数据
    // getter/setter...
}
```

```xml
<!-- 显式指定 JDBC 类型 -->
<resultMap id="documentMap" type="Document">
    <id property="id" column="id"/>
    <result property="title" column="title"/>
    <result property="content" column="content" jdbcType="CLOB"
            typeHandler="org.apache.ibatis.type.ClobTypeHandler"/>
    <result property="attachment" column="attachment" jdbcType="BLOB"
            typeHandler="org.apache.ibatis.type.BlobTypeHandler"/>
</resultMap>

<insert id="insert" parameterType="Document">
    INSERT INTO document(title, content, attachment)
    VALUES(#{title}, #{content, jdbcType=CLOB}, #{attachment, jdbcType=BLOB})
</insert>
```

**自定义 TypeHandler 处理大文本（推荐）：**

```java
public class LongTextTypeHandler extends BaseTypeHandler<String> {
    @Override
    public void setNonNullParameter(PreparedStatement ps, int i,
            String parameter, JdbcType jdbcType) throws SQLException {
        // 使用流方式写入大文本
        StringReader reader = new StringReader(parameter);
        ps.setCharacterStream(i, reader, parameter.length());
    }

    @Override
    public String getNullableResult(ResultSet rs, String columnName) throws SQLException {
        Clob clob = rs.getClob(columnName);
        return clob != null ? clob.getSubString(1, (int) clob.length()) : null;
    }
    // 其他 getNullableResult 重载...
}
```

---

**Q30：MyBatis 中如何实现读写分离？**

**答：**

**思路：** 通过 MyBatis 插件拦截 `Executor.query()` 和 `Executor.update()`，根据操作类型路由到不同的数据源。

```java
// 1. 数据源路由 key 持有者
public class DataSourceContextHolder {
    private static final ThreadLocal<String> CONTEXT = new ThreadLocal<>();

    public static void setDataSourceType(String type) {
        CONTEXT.set(type);
    }

    public static String getDataSourceType() {
        return CONTEXT.get();
    }

    public static void clear() {
        CONTEXT.remove();
    }
}

// 2. 动态数据源
public class DynamicDataSource extends AbstractRoutingDataSource {
    @Override
    protected Object determineCurrentLookupKey() {
        return DataSourceContextHolder.getDataSourceType();
    }
}

// 3. MyBatis 插件拦截
@Intercepts({
    @Signature(type = Executor.class, method = "update", args = {MappedStatement.class, Object.class}),
    @Signature(type = Executor.class, method = "query", args = {MappedStatement.class, Object.class, RowBounds.class, ResultHandler.class})
})
public class ReadWriteSplittingPlugin implements Interceptor {
    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        String methodName = invocation.getMethod().getName();
        try {
            if ("query".equals(methodName)) {
                DataSourceContextHolder.setDataSourceType("read");  // 读库
            } else {
                DataSourceContextHolder.setDataSourceType("write"); // 写库
            }
            return invocation.proceed();
        } finally {
            DataSourceContextHolder.clear();
        }
    }
}
```

**或使用现成方案：** ShardingSphere-JDBC、MyCat 等中间件，提供更完善的读写分离支持。

---

## 九、MyBatis-Spring 整合

**Q31：MyBatis 与 Spring 整合的核心原理是什么？**

**答：**

**核心组件：**

| 组件 | 作用 |
|------|------|
| `SqlSessionFactoryBean` | 创建 `SqlSessionFactory`，替代原生 Builder |
| `MapperScannerConfigurer` | 扫描 Mapper 接口并注册为 Spring Bean |
| `SqlSessionTemplate` | 线程安全的 SqlSession 实现，管理生命周期 |
| `@MapperScan` | 注解方式扫描 Mapper 接口 |

```java
// Spring Boot 配置类
@Configuration
@MapperScan("com.example.mapper")  // 扫描 Mapper 接口
public class MyBatisConfig {
    // Spring Boot 自动配置 DataSource 和 SqlSessionFactory
}
```

```yaml
# application.yml 配置
mybatis:
  mapper-locations: classpath:mapper/*.xml
  type-aliases-package: com.example.entity
  configuration:
    map-underscore-to-camel-case: true
    lazy-loading-enabled: true
    cache-enabled: true
```

**整合后的工作流程：**

```
Spring 容器启动
  → @MapperScan 扫描 Mapper 接口
    → MapperFactoryBean 为每个接口创建 MapperProxy 代理
      → 注入 SqlSessionTemplate（线程安全的 SqlSession）
        → 代理方法调用 → SqlSessionTemplate → Executor → 执行 SQL
```

**SqlSessionTemplate 的线程安全机制：**

```java
// SqlSessionTemplate 内部使用 SqlSessionHolder（ThreadLocal + 事务感知）
// 同一事务内复用同一个 SqlSession，不同事务/线程创建新的 SqlSession
// 从而实现了线程安全，同时保留了事务内的一级缓存
```

> 💡 **关键点**：Spring 整合后，SqlSession 的生命周期由 Spring 事务管理器控制，开发者无需手动 open/close。

---

**Q32：MyBatis-Spring 中 `@Mapper` 和 `@MapperScan` 有什么区别？**

**答：**

| 对比维度 | `@Mapper` | `@MapperScan` |
|---------|----------|--------------|
| 作用位置 | Mapper 接口上 | 配置类上 |
| 作用范围 | 单个接口 | 批量扫描包路径 |
| 配置方式 | 每个接口需单独标注 | 一个注解扫描整个包 |
| 适用场景 | Mapper 接口较少 | 企业级项目（推荐） |

```java
// 方式一：@Mapper（每个接口都需要标注）
@Mapper
public interface UserMapper {
    User selectById(Long id);
}

@Mapper
public interface OrderMapper {
    Order selectById(Long id);
}

// 方式二：@MapperScan（推荐，一次配置）
@Configuration
@MapperScan("com.example.mapper")
public class MyBatisConfig {
    // 自动扫描 com.example.mapper 包下所有接口
}
```

> 💡 **最佳实践**：使用 `@MapperScan` 统一扫描，避免遗漏标注。

---

**Q33：MyBatis 中 `resultType` 和 `resultMap` 如何选择？能否同时使用？**

**答：**

| 对比 | `resultType` | `resultMap` |
|------|-------------|-------------|
| 定义方式 | 直接指定 Java 类型 | 需要单独定义 `<resultMap>` |
| 映射规则 | 自动映射（列名 → 属性名） | 手动指定映射关系 |
| 适用场景 | 简单查询、列名与属性名一致 | 复杂映射、关联查询、列名不一致 |
| 灵活性 | 低 | 高 |

```xml
<!-- resultType：简单场景 -->
<select id="selectById" resultType="com.example.entity.User">
    SELECT * FROM user WHERE id = #{id}
</select>

<!-- resultMap：复杂场景 -->
<select id="selectUserDetail" resultMap="userDetailMap">
    SELECT u.*, d.name AS dept_name
    FROM user u LEFT JOIN department d ON u.dept_id = d.id
    WHERE u.id = #{id}
</select>
```

**不能同时使用**：`resultType` 和 `resultMap` 互斥，只能选择一个。

**自动映射行为控制：**

```xml
<settings>
    <!-- 自动映射行为：NONE | PARTIAL（默认） | FULL -->
    <setting name="autoMappingBehavior" value="PARTIAL"/>
</settings>
```

| 值 | 行为 |
|----|------|
| NONE | 禁用自动映射 |
| PARTIAL（默认） | 仅映射无嵌套的简单结果 |
| FULL | 映射所有结果（包括嵌套） |

---

**Q34：MyBatis 中 `#{}` 占位符在预编译时如何处理特殊字符？**

**答：**
`#{}` 使用 `PreparedStatement` 的 `setXxx()` 方法设置参数，JDBC 驱动会自动处理特殊字符转义。

```java
// 用户输入：O'Brien（包含单引号）
// SQL 模板：SELECT * FROM user WHERE name = ?
// PreparedStatement.setString(1, "O'Brien")
// 最终执行：SELECT * FROM user WHERE name = 'O''Brien'（JDBC 自动转义）
```

```java
// LIKE 查询中的特殊字符转义
public List<User> selectByLikeName(String keyword) {
    // 手动转义 LIKE 特殊字符
    String escapedKeyword = keyword
        .replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_");
    return mapper.selectByLikeName("%" + escapedKeyword + "%");
}
```

```xml
<select id="selectByLikeName" resultType="User">
    SELECT * FROM user WHERE user_name LIKE #{keyword} ESCAPE '\\'
</select>
```

---

**Q35：MyBatis 中如何实现数据库切换（多数据库支持）？**

**答：**

```xml
<!-- 1. 配置 databaseIdProvider -->
<databaseIdProvider type="DB_VENDOR">
    <property name="MySQL" value="mysql"/>
    <property name="Oracle" value="oracle"/>
    <property name="PostgreSQL" value="postgresql"/>
</databaseIdProvider>

<!-- 2. 在 SQL 语句中使用 databaseId 属性 -->
<!-- MySQL 版本 -->
<select id="selectByPage" databaseId="mysql" resultType="User">
    SELECT * FROM user LIMIT #{offset}, #{limit}
</select>

<!-- Oracle 版本 -->
<select id="selectByPage" databaseId="oracle" resultType="User">
    SELECT * FROM (
        SELECT ROWNUM rn, t.* FROM (
            SELECT * FROM user
        ) t WHERE ROWNUM &lt;= #{end}
    ) WHERE rn &gt; #{start}
</select>

<!-- 通用版本（无 databaseId） -->
<select id="selectByPage" resultType="User">
    SELECT * FROM user
</select>
```

**MyBatis 选择规则：**
1. 优先匹配精确 `databaseId` 的语句
2. 若有动态 SQL 且 `databaseId` 匹配，使用该语句
3. 否则使用无 `databaseId` 的语句

---

## 附录：快速索引

| 编号 | 问题 | 类别 |
|------|------|------|
| Q1 | 什么是 MyBatis？核心特性？ | 基础概念 |
| Q2 | `#{}` 和 `${}` 的区别？ | 基础概念 |
| Q3 | MyBatis 的工作原理？ | 基础概念 |
| Q4 | 一级缓存和二级缓存区别？ | 缓存机制 |
| Q5 | Mapper 接口工作原理？ | 基础概念 |
| Q6 | 全局配置文件常用配置项？ | 核心配置 |
| Q7 | `<resultMap>` 的作用？ | 核心配置 |
| Q8 | XML 和注解映射的优缺点？ | 核心配置 |
| Q9 | 如何获取自增主键？ | SQL 映射 |
| Q10 | 如何传递多个参数？ | SQL 映射 |
| Q11 | 模糊查询有几种写法？ | SQL 映射 |
| Q12 | 如何处理枚举类型映射？ | SQL 映射 |
| Q13 | 动态 SQL 常用标签？ | 动态 SQL |
| Q14 | `<where>` 和 `<trim>` 的区别？ | 动态 SQL |
| Q15 | `<foreach>` 详细用法？ | 动态 SQL |
| Q16 | `<if test="">` 判断规则？ | 动态 SQL |
| Q17 | 二级缓存如何配置和使用？ | 缓存机制 |
| Q18 | 一级缓存失效场景？ | 缓存机制 |
| Q19 | 延迟加载如何配置？ | 高级映射 |
| Q20 | 关联查询两种方式？ | 高级映射 |
| Q21 | 一对多/多对多映射？ | 高级映射 |
| Q22 | 鉴别器使用场景？ | 高级映射 |
| Q23 | 插件机制原理？ | 插件扩展 |
| Q24 | PageHelper 原理？ | 插件扩展 |
| Q25 | MyBatis-Plus 区别？ | 插件扩展 |
| Q26 | 性能优化手段？ | 性能优化 |
| Q27 | 如何避免 SQL 注入？ | 性能优化 |
| Q28 | 事务管理机制？ | 性能优化 |
| Q29 | 大字段处理？ | 性能优化 |
| Q30 | 如何实现读写分离？ | 性能优化 |
| Q31 | Spring 整合原理？ | 整合 |
| Q32 | `@Mapper` vs `@MapperScan`？ | 整合 |
| Q33 | `resultType` vs `resultMap`？ | 整合 |
| Q34 | `#{}` 如何处理特殊字符？ | 整合 |
| Q35 | 多数据库切换？ | 整合 |

---

> 📝 **文档说明**：本文档共覆盖 **35 个 MyBatis 高频面试题**，涵盖基础概念、核心配置、SQL 映射、动态 SQL、缓存机制、高级映射、插件扩展、性能优化和 Spring 整合九大分类。建议按顺序学习，先掌握基础概念（Q1-Q5），再深入各模块。