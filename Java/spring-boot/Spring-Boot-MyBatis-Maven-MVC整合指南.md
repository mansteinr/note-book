# Spring Boot + MyBatis + Maven 整合构建 MVC 框架完整指南

## 目录
1. [环境搭建](#环境搭建)
2. [项目结构设计](#项目结构设计)
3. [核心依赖配置](#核心依赖配置)
4. [数据库连接配置](#数据库连接配置)
5. [实体类设计](#实体类设计)
6. [数据访问层实现](#数据访问层实现)
7. [服务层开发](#服务层开发)
8. [控制器实现](#控制器实现)
9. [事务管理配置](#事务管理配置)
10. [异常处理机制](#异常处理机制)
11. [单元测试方法](#单元测试方法)
12. [项目打包与部署](#项目打包与部署)

---

## 环境搭建

### 1.1 JDK 版本要求
- **推荐版本**: JDK 17 或 JDK 21（LTS版本）
- **最低要求**: JDK 8（Spring Boot 3.x 要求 JDK 17+）
- **下载地址**: [Oracle JDK](https://www.oracle.com/java/technologies/downloads/) 或 [OpenJDK](https://adoptium.net/)

### 1.2 Maven 配置
#### 1.2.1 下载安装 Maven
- 下载地址: [Apache Maven](https://maven.apache.org/download.cgi)
- 配置环境变量:
  - `MAVEN_HOME`: Maven安装目录
  - `Path`: 添加 `%MAVEN_HOME%\bin`

#### 1.2.2 验证 Maven 安装
```bash
mvn -v
```

#### 1.2.3 配置阿里云镜像（国内加速）
编辑 `~/.m2/settings.xml` 或 Maven安装目录下的 `conf/settings.xml`:

```xml
<mirrors>
  <mirror>
    <id>aliyunmaven</id>
    <mirrorOf>*</mirrorOf>
    <name>阿里云公共仓库</name>
    <url>https://maven.aliyun.com/repository/public</url>
  </mirror>
</mirrors>
```

### 1.3 Spring Boot 初始化
#### 方式一：使用 Spring Initializr
1. 访问 [Spring Initializr](https://start.spring.io/)
2. 配置项目参数:
   - Project: Maven Project
   - Language: Java
   - Spring Boot: 3.2.x（或最新稳定版）
   - Project Metadata: 填写 Group、Artifact、Name
   - Packaging: Jar
   - Java: 17
3. 添加依赖:
   - Spring Web
   - MyBatis Framework
   - MySQL Driver
   - Lombok（可选，推荐）
4. 点击 Generate 下载项目

#### 方式二：使用 IDE 创建
- IntelliJ IDEA: New Project → Spring Initializr
- Eclipse: Spring Tool Suite (STS)

---

## 项目结构设计

### 2.1 标准 MVC 项目结构
```
src/
├── main/
│   ├── java/
│   │   └── com/
│   │       └── example/
│   │           └── demo/
│   │               ├── DemoApplication.java          # 启动类
│   │               ├── config/                        # 配置类
│   │               │   ├── MyBatisConfig.java
│   │               │   └── TransactionConfig.java
│   │               ├── controller/                    # 控制器层
│   │               │   └── UserController.java
│   │               ├── service/                       # 服务层
│   │               │   ├── UserService.java
│   │               │   └── impl/
│   │               │       └── UserServiceImpl.java
│   │               ├── mapper/                        # 数据访问层
│   │               │   └── UserMapper.java
│   │               ├── entity/                        # 实体类
│   │               │   └── User.java
│   │               ├── dto/                           # 数据传输对象
│   │               │   ├── UserDTO.java
│   │               │   └── UserQueryDTO.java
│   │               ├── vo/                            # 视图对象
│   │               │   └── UserVO.java
│   │               ├── common/                        # 公共类
│   │               │   ├── Result.java
│   │               │   └── ResultCode.java
│   │               └── exception/                     # 异常处理
│   │                   ├── BusinessException.java
│   │                   └── GlobalExceptionHandler.java
│   └── resources/
│       ├── mapper/                                    # MyBatis XML映射文件
│       │   └── UserMapper.xml
│       ├── application.yml                           # 配置文件
│       └── application-dev.yml                       # 开发环境配置
└── test/
    └── java/
        └── com/
            └── example/
                └── demo/
                    └── UserServiceTest.java
```

### 2.2 各层职责说明
- **Controller**: 接收HTTP请求，参数校验，调用Service，返回响应
- **Service**: 业务逻辑处理，事务控制
- **Mapper**: 数据库操作
- **Entity**: 数据库表对应实体
- **DTO**: 数据传输对象
- **VO**: 视图对象

---

## 核心依赖配置

### 3.1 pom.xml 完整配置
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
        <relativePath/>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>demo</artifactId>
    <version>1.0.0</version>
    <name>demo</name>
    <description>Demo project for Spring Boot + MyBatis</description>

    <properties>
        <java.version>17</java.version>
        <mybatis-spring-boot.version>3.0.3</mybatis-spring-boot.version>
    </properties>

    <dependencies>
        <!-- Spring Boot Starter Web -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- MyBatis Spring Boot Starter -->
        <dependency>
            <groupId>org.mybatis.spring.boot</groupId>
            <artifactId>mybatis-spring-boot-starter</artifactId>
            <version>${mybatis-spring-boot.version}</version>
        </dependency>

        <!-- MySQL Driver -->
        <dependency>
            <groupId>com.mysql</groupId>
            <artifactId>mysql-connector-j</artifactId>
            <scope>runtime</scope>
        </dependency>

        <!-- Spring Boot Starter Validation (参数校验) -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>

        <!-- Spring Boot Starter AOP (事务管理) -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-aop</artifactId>
        </dependency>

        <!-- Lombok (简化代码) -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>

        <!-- Spring Boot Starter Test -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>

        <!-- MyBatis Plus (可选，增强MyBatis功能) -->
        <!--
        <dependency>
            <groupId>com.baomidou</groupId>
            <artifactId>mybatis-plus-boot-starter</artifactId>
            <version>3.5.5</version>
        </dependency>
        -->
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

---

## 数据库连接配置

### 4.1 application.yml 配置
```yaml
server:
  port: 8080

spring:
  application:
    name: demo
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://localhost:3306/demo_db?useUnicode=true&characterEncoding=utf-8&useSSL=false&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true
    username: root
    password: root
    hikari:
      minimum-idle: 5
      maximum-pool-size: 20
      auto-commit: true
      idle-timeout: 30000
      max-lifetime: 1800000
      connection-timeout: 30000

mybatis:
  mapper-locations: classpath:mapper/*.xml
  type-aliases-package: com.example.demo.entity
  configuration:
    map-underscore-to-camel-case: true
    cache-enabled: false
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl

logging:
  level:
    com.example.demo.mapper: debug
```

### 4.2 多环境配置
创建 `application-dev.yml` 和 `application-prod.yml`:

**application-dev.yml**:
```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/demo_db?useUnicode=true&characterEncoding=utf-8&useSSL=false&serverTimezone=Asia/Shanghai
    username: root
    password: root
```

**application-prod.yml**:
```yaml
spring:
  datasource:
    url: jdbc:mysql://prod-server:3306/demo_db?useUnicode=true&characterEncoding=utf-8&useSSL=true&serverTimezone=Asia/Shanghai
    username: prod_user
    password: ${DB_PASSWORD}
```

在 `application.yml` 中激活环境:
```yaml
spring:
  profiles:
    active: dev
```

### 4.3 初始化数据库
```sql
CREATE DATABASE IF NOT EXISTS demo_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE demo_db;

CREATE TABLE IF NOT EXISTS user (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(100) NOT NULL COMMENT '密码',
    email VARCHAR(100) COMMENT '邮箱',
    phone VARCHAR(20) COMMENT '手机号',
    age INT COMMENT '年龄',
    status TINYINT DEFAULT 1 COMMENT '状态: 1-启用, 0-禁用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

INSERT INTO user (username, password, email, phone, age, status) VALUES
('admin', '123456', 'admin@example.com', '13800138000', 25, 1),
('user1', '123456', 'user1@example.com', '13800138001', 28, 1),
('user2', '123456', 'user2@example.com', '13800138002', 30, 1);
```

---

## 实体类设计

### 5.1 User.java (实体类)
```java
package com.example.demo.entity;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class User {
    private Long id;
    private String username;
    private String password;
    private String email;
    private String phone;
    private Integer age;
    private Integer status;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
```

### 5.2 Result.java (统一响应结果)
```java
package com.example.demo.common;

import lombok.Data;

@Data
public class Result<T> {
    private Integer code;
    private String message;
    private T data;

    public static <T> Result<T> success(T data) {
        Result<T> result = new Result<>();
        result.setCode(200);
        result.setMessage("success");
        result.setData(data);
        return result;
    }

    public static <T> Result<T> success() {
        return success(null);
    }

    public static <T> Result<T> error(Integer code, String message) {
        Result<T> result = new Result<>();
        result.setCode(code);
        result.setMessage(message);
        return result;
    }

    public static <T> Result<T> error(String message) {
        return error(500, message);
    }
}
```

### 5.3 ResultCode.java (状态码枚举)
```java
package com.example.demo.common;

import lombok.Getter;

@Getter
public enum ResultCode {
    SUCCESS(200, "操作成功"),
    BAD_REQUEST(400, "请求参数错误"),
    UNAUTHORIZED(401, "未授权"),
    NOT_FOUND(404, "资源不存在"),
    INTERNAL_SERVER_ERROR(500, "服务器内部错误"),
    USER_NOT_FOUND(1001, "用户不存在"),
    USER_ALREADY_EXISTS(1002, "用户已存在");

    private final Integer code;
    private final String message;

    ResultCode(Integer code, String message) {
        this.code = code;
        this.message = message;
    }
}
```

---

## 数据访问层实现

### 6.1 UserMapper.java (Mapper接口)
```java
package com.example.demo.mapper;

import com.example.demo.entity.User;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface UserMapper {
    int insert(User user);

    int updateById(User user);

    int deleteById(Long id);

    User selectById(Long id);

    User selectByUsername(String username);

    List<User> selectAll();

    List<User> selectByCondition(@Param("username") String username,
                                  @Param("status") Integer status);
}
```

### 6.2 UserMapper.xml (XML映射文件)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.example.demo.mapper.UserMapper">

    <resultMap id="BaseResultMap" type="com.example.demo.entity.User">
        <id column="id" property="id" jdbcType="BIGINT"/>
        <result column="username" property="username" jdbcType="VARCHAR"/>
        <result column="password" property="password" jdbcType="VARCHAR"/>
        <result column="email" property="email" jdbcType="VARCHAR"/>
        <result column="phone" property="phone" jdbcType="VARCHAR"/>
        <result column="age" property="age" jdbcType="INTEGER"/>
        <result column="status" property="status" jdbcType="TINYINT"/>
        <result column="create_time" property="createTime" jdbcType="TIMESTAMP"/>
        <result column="update_time" property="updateTime" jdbcType="TIMESTAMP"/>
    </resultMap>

    <sql id="Base_Column_List">
        id, username, password, email, phone, age, status, create_time, update_time
    </sql>

    <insert id="insert" parameterType="com.example.demo.entity.User" useGeneratedKeys="true" keyProperty="id">
        INSERT INTO user (username, password, email, phone, age, status)
        VALUES (#{username}, #{password}, #{email}, #{phone}, #{age}, #{status})
    </insert>

    <update id="updateById" parameterType="com.example.demo.entity.User">
        UPDATE user
        <set>
            <if test="username != null">username = #{username},</if>
            <if test="password != null">password = #{password},</if>
            <if test="email != null">email = #{email},</if>
            <if test="phone != null">phone = #{phone},</if>
            <if test="age != null">age = #{age},</if>
            <if test="status != null">status = #{status},</if>
        </set>
        WHERE id = #{id}
    </update>

    <delete id="deleteById" parameterType="java.lang.Long">
        DELETE FROM user WHERE id = #{id}
    </delete>

    <select id="selectById" parameterType="java.lang.Long" resultMap="BaseResultMap">
        SELECT <include refid="Base_Column_List"/>
        FROM user
        WHERE id = #{id}
    </select>

    <select id="selectByUsername" parameterType="java.lang.String" resultMap="BaseResultMap">
        SELECT <include refid="Base_Column_List"/>
        FROM user
        WHERE username = #{username}
    </select>

    <select id="selectAll" resultMap="BaseResultMap">
        SELECT <include refid="Base_Column_List"/>
        FROM user
        ORDER BY create_time DESC
    </select>

    <select id="selectByCondition" resultMap="BaseResultMap">
        SELECT <include refid="Base_Column_List"/>
        FROM user
        <where>
            <if test="username != null and username != ''">
                AND username LIKE CONCAT('%', #{username}, '%')
            </if>
            <if test="status != null">
                AND status = #{status}
            </if>
        </where>
        ORDER BY create_time DESC
    </select>

</mapper>
```

---

## 服务层开发

### 7.1 UserService.java (Service接口)
```java
package com.example.demo.service;

import com.example.demo.entity.User;

import java.util.List;

public interface UserService {
    User create(User user);

    User update(User user);

    void delete(Long id);

    User getById(Long id);

    User getByUsername(String username);

    List<User> getAll();

    List<User> getByCondition(String username, Integer status);
}
```

### 7.2 UserServiceImpl.java (Service实现)
```java
package com.example.demo.service.impl;

import com.example.demo.entity.User;
import com.example.demo.exception.BusinessException;
import com.example.demo.mapper.UserMapper;
import com.example.demo.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {

    private final UserMapper userMapper;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public User create(User user) {
        User existUser = userMapper.selectByUsername(user.getUsername());
        if (existUser != null) {
            throw new BusinessException("用户名已存在");
        }
        userMapper.insert(user);
        return user;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public User update(User user) {
        User existUser = userMapper.selectById(user.getId());
        if (existUser == null) {
            throw new BusinessException("用户不存在");
        }
        userMapper.updateById(user);
        return userMapper.selectById(user.getId());
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void delete(Long id) {
        User user = userMapper.selectById(id);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        userMapper.deleteById(id);
    }

    @Override
    public User getById(Long id) {
        User user = userMapper.selectById(id);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        return user;
    }

    @Override
    public User getByUsername(String username) {
        return userMapper.selectByUsername(username);
    }

    @Override
    public List<User> getAll() {
        return userMapper.selectAll();
    }

    @Override
    public List<User> getByCondition(String username, Integer status) {
        return userMapper.selectByCondition(username, status);
    }
}
```

---

## 控制器实现

### 8.1 UserController.java (RESTful API)
```java
package com.example.demo.controller;

import com.example.demo.common.Result;
import com.example.demo.entity.User;
import com.example.demo.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @PostMapping
    public Result<User> create(@RequestBody User user) {
        User createdUser = userService.create(user);
        return Result.success(createdUser);
    }

    @PutMapping("/{id}")
    public Result<User> update(@PathVariable Long id, @RequestBody User user) {
        user.setId(id);
        User updatedUser = userService.update(user);
        return Result.success(updatedUser);
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        userService.delete(id);
        return Result.success();
    }

    @GetMapping("/{id}")
    public Result<User> getById(@PathVariable Long id) {
        User user = userService.getById(id);
        return Result.success(user);
    }

    @GetMapping
    public Result<List<User>> getAll(@RequestParam(required = false) String username,
                                      @RequestParam(required = false) Integer status) {
        List<User> users;
        if (username != null || status != null) {
            users = userService.getByCondition(username, status);
        } else {
            users = userService.getAll();
        }
        return Result.success(users);
    }
}
```

---

## 事务管理配置

### 9.1 启用事务管理
在启动类添加 `@EnableTransactionManagement`:
```java
package com.example.demo;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.transaction.annotation.EnableTransactionManagement;

@SpringBootApplication
@EnableTransactionManagement
@MapperScan("com.example.demo.mapper")
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

### 9.2 @Transactional 注解使用
```java
@Service
public class UserServiceImpl implements UserService {

    @Transactional(rollbackFor = Exception.class)
    public User create(User user) {
        userMapper.insert(user);
        return user;
    }

    @Transactional(rollbackFor = Exception.class, propagation = Propagation.REQUIRES_NEW)
    public void batchInsert(List<User> users) {
        users.forEach(userMapper::insert);
    }
}
```

---

## 异常处理机制

### 10.1 BusinessException.java (业务异常)
```java
package com.example.demo.exception;

import lombok.Getter;

@Getter
public class BusinessException extends RuntimeException {
    private final Integer code;

    public BusinessException(String message) {
        super(message);
        this.code = 500;
    }

    public BusinessException(Integer code, String message) {
        super(message);
        this.code = code;
    }
}
```

### 10.2 GlobalExceptionHandler.java (全局异常处理)
```java
package com.example.demo.exception;

import com.example.demo.common.Result;
import lombok.extern.slf4j.Slf4j;
import org.springframework.validation.BindException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public Result<Void> handleBusinessException(BusinessException e) {
        log.error("业务异常: {}", e.getMessage());
        return Result.error(e.getCode(), e.getMessage());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public Result<Void> handleValidationException(MethodArgumentNotValidException e) {
        FieldError fieldError = e.getBindingResult().getFieldError();
        String message = fieldError != null ? fieldError.getDefaultMessage() : "参数校验失败";
        log.error("参数校验异常: {}", message);
        return Result.error(400, message);
    }

    @ExceptionHandler(BindException.class)
    public Result<Void> handleBindException(BindException e) {
        FieldError fieldError = e.getFieldError();
        String message = fieldError != null ? fieldError.getDefaultMessage() : "参数绑定失败";
        log.error("参数绑定异常: {}", message);
        return Result.error(400, message);
    }

    @ExceptionHandler(Exception.class)
    public Result<Void> handleException(Exception e) {
        log.error("系统异常: ", e);
        return Result.error("系统内部错误");
    }
}
```

---

## 单元测试方法

### 11.1 UserServiceTest.java (Service层测试)
```java
package com.example.demo;

import com.example.demo.entity.User;
import com.example.demo.service.UserService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.List;

@SpringBootTest
public class UserServiceTest {

    @Autowired
    private UserService userService;

    @Test
    public void testCreateUser() {
        User user = new User();
        user.setUsername("testuser");
        user.setPassword("123456");
        user.setEmail("test@example.com");
        user.setAge(25);
        user.setStatus(1);

        User createdUser = userService.create(user);
        System.out.println("创建用户成功: " + createdUser);
    }

    @Test
    public void testGetAllUsers() {
        List<User> users = userService.getAll();
        users.forEach(System.out::println);
    }

    @Test
    public void testGetUserById() {
        User user = userService.getById(1L);
        System.out.println(user);
    }

    @Test
    public void testUpdateUser() {
        User user = new User();
        user.setId(1L);
        user.setEmail("updated@example.com");
        User updatedUser = userService.update(user);
        System.out.println("更新用户成功: " + updatedUser);
    }

    @Test
    public void testDeleteUser() {
        userService.delete(4L);
        System.out.println("删除用户成功");
    }
}
```

---

## 项目打包与部署

### 12.1 Maven 打包
```bash
mvn clean package
```

### 12.2 运行 JAR 包
```bash
java -jar target/demo-1.0.0.jar
```

### 12.3 指定配置文件运行
```bash
java -jar target/demo-1.0.0.jar --spring.profiles.active=prod
```

### 12.4 指定端口运行
```bash
java -jar target/demo-1.0.0.jar --server.port=8081
```

---

## 测试 API 示例

### 使用 curl 测试

```bash
# 获取所有用户
curl http://localhost:8080/api/users

# 根据ID获取用户
curl http://localhost:8080/api/users/1

# 创建用户
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","password":"123456","email":"new@example.com","age":30,"status":1}'

# 更新用户
curl -X PUT http://localhost:8080/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{"email":"updated@example.com"}'

# 删除用户
curl -X DELETE http://localhost:8080/api/users/4

# 条件查询
curl "http://localhost:8080/api/users?username=admin&status=1"
```

---

## 总结

本指南详细介绍了如何从零开始搭建一个 Spring Boot + MyBatis + Maven 的 MVC 框架项目，包括：

1. 完整的环境搭建流程
2. 标准的项目结构设计
3. 所有必要的依赖配置
4. 数据库连接和初始化
5. 各层代码的规范实现
6. 事务管理和异常处理
7. 单元测试方法
8. 打包部署流程

按照本指南操作，您可以快速构建一个功能完善、可运行的 Spring Boot Web 应用。
