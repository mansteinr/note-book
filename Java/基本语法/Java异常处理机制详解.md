# Java 异常处理机制详解

> 本文档系统介绍 Java 异常处理的完整体系，包括异常分类、处理语法、自定义异常、try-with-resources 现代特性及最佳实践。

---

## 目录

- [一、异常体系架构](#一异常体系架构)
  - [1.1 Throwable 继承结构](#11-throwable-继承结构)
  - [1.2 受检异常 vs 非受检异常](#12-受检异常-vs-非受检异常)
  - [1.3 Error 与 Exception 的区别](#13-error-与-exception-的区别)
- [二、异常处理语法](#二异常处理语法)
  - [2.1 try-catch-finally 基础语法](#21-try-catch-finally-基础语法)
  - [2.2 多异常捕获](#22-多异常捕获)
  - [2.3 try-with-resources (Java 7+)](#23-try-with-resources-java-7)
  - [2.4 throw 与 throws 关键字](#24-throw-与-throws-关键字)
- [三、自定义异常](#三自定义异常)
  - [3.1 为什么需要自定义异常](#31-为什么需要自定义异常)
  - [3.2 自定义业务异常类](#32-自定义业务异常类)
  - [3.3 多层异常包装](#33-多层异常包装)
- [四、异常处理最佳实践](#四异常处理最佳实践)
  - [4.1 异常处理原则](#41-异常处理原则)
  - [4.2 常见反模式](#42-常见反模式)
  - [4.3 日志记录规范](#43-日志记录规范)
- [五、面试高频考点](#五面试高频考点)

---

## 一、异常体系架构

### 1.1 Throwable 继承结构

Java 异常体系以 `java.lang.Throwable` 为根节点：

```
Throwable
├── Error (严重错误，程序无法恢复)
│   ├── OutOfMemoryError      - 内存溢出
│   ├── StackOverflowError    - 栈溢出（递归过深）
│   ├── NoClassDefFoundError  - 类未找到
│   └── ...
│
└── Exception (异常，程序可处理)
    ├── RuntimeException (非受检异常，不需强制处理)
    │   ├── NullPointerException       - 空指针
    │   ├── ArrayIndexOutOfBoundsException - 数组越界
    │   ├── ClassCastException          - 类型转换异常
    │   ├── IllegalArgumentException     - 非法参数
    │   ├── IllegalStateException        - 非法状态
    │   ├── ConcurrentModificationException - 并发修改
    │   └── ...
    │
    ├── IOException (受检异常，需强制处理)
    │   ├── FileNotFoundException  - 文件未找到
    │   ├── SocketException        - Socket 异常
    │   └── ...
    │
    ├── SQLException     - 数据库异常
    ├── ParseException   - 解析异常
    ├── ClassNotFoundException - 类未找到
    └── ...
```

### 1.2 受检异常 vs 非受检异常

**非受检异常（Unchecked Exception）：**
- 继承自 `RuntimeException` 的异常
- 编译器不强制要求处理
- 通常由程序员疏忽或逻辑错误导致
- 建议在代码中主动防御

**受检异常（Checked Exception）：**
- 继承自 `Exception` 但不是 `RuntimeException`
- 编译器强制要求处理（try-catch 或 throws 声明）
- 通常由外部因素导致（IO、网络、数据库等）

```java
/**
 * 受检异常必须处理
 */
public class ExceptionDemo {
    
    // 方式一：try-catch 捕获处理
    public void readFile() {
        try {
            FileReader reader = new FileReader("file.txt");
            BufferedReader br = new BufferedReader(reader);
            String line;
            while ((line = br.readLine()) != null) {
                System.out.println(line);
            }
            br.close();
        } catch (IOException e) {
            // 必须处理
            System.err.println("读取文件失败: " + e.getMessage());
        }
    }
    
    // 方式二：throws 声明向上抛
    public void readFile2() throws IOException {
        FileReader reader = new FileReader("file.txt");
        BufferedReader br = new BufferedReader(reader);
        String line = br.readLine();
        br.close();
    }
}
```

### 1.3 Error 与 Exception 的区别

| 特性 | Error | Exception |
|------|-------|-----------|
| **处理方式** | 不应捕获，程序无法恢复 | 可以且应该处理 |
| **常见场景** | 内存溢出、栈溢出 | 空指针、IO 失败、业务校验 |
| **是否可处理** | 不可 | 可 |

---

## 二、异常处理语法

### 2.1 try-catch-finally 基础语法

```java
/**
 * try-catch-finally 完整结构
 */
public class TryCatchFinally {
    
    // 最基本的 try-catch
    public void basicTryCatch() {
        int[] arr = {1, 2, 3};
        try {
            System.out.println(arr[5]); // 数组越界
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("数组越界: " + e.getMessage());
        }
        System.out.println("程序继续执行");
    }
    
    // 带 finally 的结构
    public void withFinally() {
        Connection conn = null;
        try {
            conn = getConnection();
            conn.executeQuery("SELECT * FROM users");
        } catch (SQLException e) {
            System.err.println("数据库操作失败: " + e.getMessage());
        } finally {
            // 无论是否异常，finally 都执行
            if (conn != null) {
                try {
                    conn.close();
                } catch (SQLException e) {
                    System.err.println("关闭连接失败: " + e.getMessage());
                }
            }
        }
    }
    
    // 模拟获取数据库连接
    private Connection getConnection() {
        // 实际项目中从连接池获取
        return null;
    }
}
```

### 2.2 多异常捕获

```java
/**
 * 多异常处理方式
 */
public class MultiCatch {
    
    // 方式一：多个 catch 块
    public void multipleCatch() {
        try {
            parseAndProcess();
        } catch (NumberFormatException e) {
            System.err.println("数字格式错误: " + e.getMessage());
        } catch (IllegalArgumentException e) {
            System.err.println("参数非法: " + e.getMessage());
        } catch (Exception e) {
            // 兜底处理所有异常
            System.err.println("未知错误: " + e.getMessage());
        }
    }
    
    // 方式二：JDK 7+ 多异常合并捕获
    public void multiCatchJava7() {
        try {
            parseAndProcess();
        } catch (NumberFormatException | IllegalArgumentException e) {
            // 相同处理逻辑
            System.err.println("输入错误: " + e.getMessage());
        } catch (Exception e) {
            System.err.println("未知错误: " + e.getMessage());
        }
    }
    
    // 多 catch 注意事项：子类异常必须在前
    public void catchOrder() {
        try {
            riskyOperation();
        } catch (NullPointerException e) {
            // 子类异常在前
        } catch (RuntimeException e) {
            // 父类异常在后
        }
        // 错误顺序会导致编译错误或子类异常被父类捕获
    }
    
    private void parseAndProcess() {
        String num = "abc";
        int value = Integer.parseInt(num); // 抛出 NumberFormatException
        if (value < 0) {
            throw new IllegalArgumentException("负数不允许");
        }
    }
    
    private void riskyOperation() {
        throw new NullPointerException("test");
    }
}
```

### 2.3 try-with-resources (Java 7+)

**自动关闭实现了 `AutoCloseable` 接口的资源：**

```java
/**
 * try-with-resources 使用示例
 */
public class TryWithResourcesDemo {
    
    // 单个资源
    public String readFile(String path) throws IOException {
        // 自动关闭 FileReader，无需 finally
        try (FileReader reader = new FileReader(path)) {
            char[] buffer = new char[1024];
            StringBuilder sb = new StringBuilder();
            int n;
            while ((n = reader.read(buffer)) != -1) {
                sb.append(buffer, 0, n);
            }
            return sb.toString();
        }
    }
    
    // 多个资源（按声明顺序的逆序关闭）
    public void copyFile(String srcPath, String destPath) throws IOException {
        try (FileInputStream fis = new FileInputStream(srcPath);
             FileOutputStream fos = new FileOutputStream(destPath)) {
            byte[] buffer = new byte[8192];
            int bytesRead;
            while ((bytesRead = fis.read(buffer)) != -1) {
                fos.write(buffer, 0, bytesRead);
            }
        }
        // fis 和 fos 都会自动关闭
    }
    
    // 自定义 AutoCloseable 资源
    public class MyResource implements AutoCloseable {
        @Override
        public void close() throws Exception {
            System.out.println("资源已自动关闭");
        }
        
        public void doWork() {
            System.out.println("执行任务");
        }
    }
    
    public void useCustomResource() {
        try (MyResource resource = new MyResource()) {
            resource.doWork();
        } catch (Exception e) {
            System.err.println("异常: " + e.getMessage());
        }
    }
}
```

### 2.4 throw 与 throws 关键字

```java
/**
 * throw 和 throws 的使用
 */
public class ThrowThrowsDemo {
    
    // throws 声明方法可能抛出的异常
    public void validateAge(int age) throws IllegalArgumentException {
        if (age < 0 || age > 150) {
            // throw 显式抛出异常
            throw new IllegalArgumentException("年龄必须在 0-150 之间，当前: " + age);
        }
        System.out.println("年龄合法: " + age);
    }
    
    // 在 catch 中重新抛出
    public void processFile(String path) throws IOException {
        try {
            readLargeFile(path);
        } catch (IOException e) {
            // 可以包装后重新抛出
            throw new IOException("处理文件失败: " + path, e);
        }
    }
    
    // 捕获后包装成业务异常
    public void processOrder(Order order) {
        try {
            validateOrder(order);
            saveOrder(order);
        } catch (SQLException e) {
            // 将底层异常包装成业务异常
            throw new BusinessException("订单保存失败", e);
        }
    }
    
    // try-catch-finally 中重新抛出
    public void complexException() throws Exception {
        Resource resource = null;
        Exception caughtException = null;
        try {
            resource = ResourceManager.acquire();
            resource.doSomething();
        } catch (Exception e) {
            caughtException = e;
            throw e; // 重新抛出
        } finally {
            if (resource != null) {
                try {
                    resource.cleanup();
                } catch (Exception cleanupEx) {
                    if (caughtException != null) {
                        // 将清理异常作为抑制异常附加
                        caughtException.addSuppressed(cleanupEx);
                    } else {
                        throw cleanupEx;
                    }
                }
            }
        }
    }
}
```

---

## 三、自定义异常

### 3.1 为什么需要自定义异常

1. **表达业务语义**：标准异常无法清晰表达业务场景
2. **区分系统异常和业务异常**：便于统一异常处理
3. **携带额外信息**：可以包含错误码、上下文数据等
4. **统一错误码体系**：便于前端展示和问题定位

### 3.2 自定义业务异常类

```java
/**
 * 基础业务异常类
 */
public class BusinessException extends RuntimeException {
    
    private final String errorCode;
    private final Map<String, Object> extraData;
    
    public BusinessException(String message, String errorCode) {
        super(message);
        this.errorCode = errorCode;
        this.extraData = new HashMap<>();
    }
    
    public BusinessException(String message, String errorCode, Throwable cause) {
        super(message, cause);
        this.errorCode = errorCode;
        this.extraData = new HashMap<>();
    }
    
    public String getErrorCode() {
        return errorCode;
    }
    
    public Map<String, Object> getExtraData() {
        return Collections.unmodifiableMap(extraData);
    }
    
    public BusinessException withExtraData(String key, Object value) {
        this.extraData.put(key, value);
        return this;
    }
}

/**
 * 用户不存在异常
 */
public class UserNotFoundException extends BusinessException {
    
    public UserNotFoundException(String userId) {
        super("用户不存在", "USER_NOT_FOUND");
        withExtraData("userId", userId);
    }
}

/**
 * 库存不足异常
 */
public class InsufficientStockException extends BusinessException {
    
    private final int required;
    private final int available;
    
    public InsufficientStockException(String productId, int required, int available) {
        super("库存不足", "INSUFFICIENT_STOCK");
        this.required = required;
        this.available = available;
        withExtraData("productId", productId);
        withExtraData("required", required);
        withExtraData("available", available);
    }
    
    public int getRequired() {
        return required;
    }
    
    public int getAvailable() {
        return available;
    }
}

/**
 * 自定义异常使用示例
 */
public class CustomExceptionDemo {
    
    // 定义错误码常量
    public static final String SYSTEM_ERROR = "SYSTEM_ERROR";
    public static final String USER_NOT_FOUND = "USER_NOT_FOUND";
    public static final String INVALID_PARAM = "INVALID_PARAM";
    public static final String INSUFFICIENT_STOCK = "INSUFFICIENT_STOCK";
    
    // 使用业务异常
    public void purchase(String userId, String productId, int quantity) {
        // 1. 校验用户
        User user = userService.findById(userId);
        if (user == null) {
            throw new UserNotFoundException(userId);
        }
        
        // 2. 校验库存
        int stock = inventoryService.getStock(productId);
        if (stock < quantity) {
            throw new InsufficientStockException(productId, quantity, stock);
        }
        
        // 3. 创建订单...
    }
    
    // 统一异常处理
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<?> handleBusinessException(BusinessException e) {
        log.warn("业务异常: code={}, message={}", e.getErrorCode(), e.getMessage());
        
        ErrorResponse response = ErrorResponse.builder()
            .code(e.getErrorCode())
            .message(e.getMessage())
            .data(e.getExtraData())
            .build();
        
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
            .body(response);
    }
}
```

### 3.3 多层异常包装

```java
/**
 * 异常包装与传递
 */
public class ExceptionWrapping {
    
    // 底层抛出原始异常
    public void dataAccess() throws DataAccessException {
        try {
            jdbcTemplate.update("INSERT INTO users ...");
        } catch (DataAccessException e) {
            log.error("数据库操作失败", e);
            throw new DataAccessException("用户数据写入失败", e);
        }
    }
    
    // 中间层包装成服务异常
    public void businessLogic(String userName) {
        try {
            dataAccess();
        } catch (DataAccessException e) {
            throw new ServiceException("用户创建失败", e);
        }
    }
    
    // 上层再次包装成业务异常
    public void createUser(String userName) {
        try {
            businessLogic(userName);
        } catch (ServiceException e) {
            throw new BusinessException("USER_CREATE_FAILED", "创建用户 " + userName + " 失败", e);
        }
    }
    
    // 最终层捕获并处理
    public ResponseEntity<?> createUserEndpoint(String userName) {
        try {
            createUser(userName);
            return ResponseEntity.ok().build();
        } catch (BusinessException e) {
            log.warn("业务异常", e);
            return ResponseEntity.badRequest()
                .body(new ErrorResponse(e.getErrorCode(), e.getMessage()));
        } catch (Exception e) {
            log.error("系统异常", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(new ErrorResponse("SYSTEM_ERROR", "系统繁忙，请稍后重试"));
        }
    }
}
```

---

## 四、异常处理最佳实践

### 4.1 异常处理原则

**原则一：精确捕获**
```java
// 好：捕获具体异常
try {
    processData();
} catch (IOException e) {
    // 处理 IO 异常
} catch (ParseException e) {
    // 处理解析异常
}

// 不好：捕获 Exception（太宽泛）
try {
    processData();
} catch (Exception e) {
    // 可能掩盖其他未知错误
}
```

**原则二：不忽略异常**
```java
// 好：记录日志并处理
try {
    closeConnection();
} catch (SQLException e) {
    log.warn("关闭连接失败", e);
}

// 不好：空 catch 块
try {
    closeConnection();
} catch (SQLException e) {
    // 什么都不做
}
```

**原则三：提供上下文信息**
```java
// 好：包含关键信息
catch (IOException e) {
    throw new BusinessException("读取文件失败: " + filePath + ", 用户: " + userId, e);
}

// 不好：丢失上下文
catch (IOException e) {
    throw new BusinessException("读取失败", e);
}
```

**原则四：使用 try-with-resources**
```java
// 好：自动关闭
try (FileInputStream fis = new FileInputStream("data.bin")) {
    // 使用 fis
}

// 不好：手动关闭（容易遗漏）
FileInputStream fis = null;
try {
    fis = new FileInputStream("data.bin");
} finally {
    if (fis != null) {
        fis.close();
    }
}
```

**原则五：不要用异常做流程控制**
```java
// 好：提前判断
if (user != null && user.isActive()) {
    grantAccess(user);
}

// 不好：使用异常控制
try {
    grantAccessOrThrow(user);
} catch (InactiveUserException e) {
    // 这不是错误，是正常业务分支
}
```

### 4.2 常见反模式

**反模式一：空 catch 块**
```java
// ❌ 错误示例
try {
    saveToDatabase();
} catch (SQLException e) {
    // 空 catch - 异常被完全吞没
}
```

**反模式二：过度使用 printStackTrace**
```java
// ❌ 错误示例
try {
    processData();
} catch (Exception e) {
    e.printStackTrace(); // 输出到控制台，无法被日志系统收集
}

// ✅ 正确做法
try {
    processData();
} catch (Exception e) {
    log.error("处理数据失败", e);
}
```

**反模式三：忽略原始异常**
```java
// ❌ 错误示例
catch (SQLException e) {
    throw new RuntimeException("数据库错误"); // 丢失原始异常信息
}

// ✅ 正确做法
catch (SQLException e) {
    throw new RuntimeException("数据库错误", e); // 保留原始异常
}
```

**反模式四：catch 后不处理也不抛出**
```java
// ❌ 错误示例
public void updateUser(User user) {
    try {
        userDao.update(user);
    } catch (SQLException e) {
        // 只是打印，不处理也不向上抛
        System.out.println("错误");
    }
    // 程序继续执行，但数据可能没有更新
    sendConfirmationEmail(user); // 这会产生错误！
}

// ✅ 正确做法
public void updateUser(User user) {
    try {
        userDao.update(user);
    } catch (SQLException e) {
        throw new ServiceException("更新用户失败", e);
    }
    sendConfirmationEmail(user);
}
```

**反模式五：在循环中捕获异常**
```java
// ❌ 错误示例
for (User user : users) {
    try {
        processUser(user);
    } catch (Exception e) {
        // 单个用户失败不影响其他，但可能导致部分成功
        log.warn("用户 {} 处理失败", user.getId(), e);
    }
}

// ✅ 正确做法：根据业务需求选择
// 如果需要全部成功才成功，应该在循环外 try-catch
// 如果允许部分成功，应记录失败项，支持重试
List<String> failedIds = new ArrayList<>();
for (User user : users) {
    try {
        processUser(user);
    } catch (Exception e) {
        failedIds.add(user.getId());
    }
}
if (!failedIds.isEmpty()) {
    log.warn("部分用户处理失败: {}", failedIds);
}
```

### 4.3 日志记录规范

```java
/**
 * 异常日志记录规范
 */
public class LoggingException {
    
    // 错误的日志记录方式
    public void badLogging() {
        try {
            parseConfig();
        } catch (Exception e) {
            // 只记录消息，丢失堆栈
            System.out.println("出错了");
            
            // 只记录 message，没有堆栈
            log.error("解析配置出错: " + e.getMessage());
            
            // 同时记录 message 和堆栈
            log.error("解析配置出错: {}", e.getMessage(), e);
        }
    }
    
    // 正确的日志记录方式
    public void goodLogging() {
        try {
            parseConfig();
        } catch (IOException e) {
            // 方式一：参数化日志（推荐）
            log.error("解析配置文件失败, path={}", configPath, e);
            
            // 方式二：使用 SLF4J 占位符
            // {} 会被替换，e 作为最后一个参数会自动打印堆栈
        }
    }
    
    // 异常日志级别选择
    public void logLevelSelection() {
        try {
            riskyOperation();
        } catch (ValidationException e) {
            // warn: 业务校验失败，预期内的行为
            log.warn("参数校验失败: userId={}, reason={}", userId, e.getReason());
        } catch (IOException e) {
            // error: 外部系统异常，需要排查
            log.error("调用外部服务失败, url={}", externalUrl, e);
        }
    }
    
    // 日志记录最佳实践
    public void bestPractices() {
        try {
            processRequest(request);
        } catch (BusinessException e) {
            // 业务异常：记录关键上下文
            log.warn("业务异常, code={}, requestId={}, userId={}",
                e.getErrorCode(), request.getId(), request.getUserId());
            throw e; // 继续向上抛出
        } catch (Exception e) {
            // 系统异常：完整堆栈
            log.error("系统异常, requestId={}, userId={}",
                request.getId(), request.getUserId(), e);
            throw new ServiceException("系统繁忙", e);
        }
    }
}
```

---

## 五、面试高频考点

### 考点一：Exception 与 Error 的区别

**Q: 请描述 Exception 和 Error 的区别？**

**A:**
- `Error`：表示严重的系统级错误，如 `OutOfMemoryError`、`StackOverflowError`，程序无法恢复，不应捕获
- `Exception`：表示可预期的异常情况，分为：
  - **RuntimeException（非受检异常）**：如 `NullPointerException`、`ArrayIndexOutOfBoundsException`，编译器不强制处理
  - **Checked Exception（受检异常）**：如 `IOException`、`SQLException`，编译器强制处理

### 考点二：受检异常与非受检异常的选择

**Q: 何时使用受检异常？何时使用非受检异常？**

**A:**
- **使用非受检异常（RuntimeException）的场景**：
  - 编程错误（空指针、数组越界）
  - 不可能发生的异常（断言失败）
  - 不需要强制处理的情况
  - 框架内部异常（如 Spring 的 `DataAccessException`）

- **使用受检异常的场景**：
  - 需要调用方显式处理的外部操作（文件IO、网络调用、数据库操作）
  - 预期内的业务异常，强制调用方处理
  - 需要在方法签名中声明的异常

### 考点三：try-catch-finally 的执行顺序

**Q: try、catch、finally 的执行顺序是什么？finally 是否一定执行？**

**A:**
- **执行顺序**：try → catch → finally
- **finally 是否一定执行**：
  - ✅ 在 try/catch 正常完成时执行
  - ✅ 在 try/catch 中有 return/throw 时执行（在返回前执行）
  - ✅ 即使 catch 中再次抛出异常，finally 仍会执行
  - ❌ 只有一种情况不执行：JVM 崩溃（`System.exit()`）或断电

```java
// finally 中修改返回值的陷阱
public int test() {
    int x = 0;
    try {
        x = 1;
        return x; // 注意：这里返回的是 1，但 finally 会在返回前执行
    } finally {
        x = 2; // 修改 x，但不影响 try 中已计算好的返回值
    }
    // 返回 1，不是 2
}

// finally 中返回的陷阱
public int test2() {
    try {
        return 1;
    } finally {
        return 2; // 这会覆盖 try 中的 return，返回 2
    }
}
```

### 考点四：异常链的作用

**Q: 什么是异常链？为什么要保留原始异常？**

**A:**
- **异常链**：在捕获一个异常后，创建一个新的异常并将原始异常作为 cause 传递，形成异常链条
- **目的**：保留完整的异常信息，便于排查问题
- **实现**：使用构造器 `Exception(message, cause)` 或 `initCause()`

```java
// 正确的异常链
public void updateUser(User user) {
    try {
        userRepository.save(user);
    } catch (DataAccessException e) {
        // 包装成业务异常，保留原始异常
        throw new ServiceException("用户更新失败", e);
    }
}

// 错误：丢失原始异常
public void badExample(User user) {
    try {
        userRepository.save(user);
    } catch (DataAccessException e) {
        throw new ServiceException("用户更新失败"); // 丢失了 DataAccessException
    }
}
```

### 考点五：try-with-resources 的原理

**Q: try-with-resources 是如何实现自动关闭的？**

**A:**
- **原理**：编译器将 try-with-resources 转换为 try-finally 结构，在 finally 块中调用 `close()` 方法
- **前提**：资源类必须实现 `AutoCloseable` 接口
- **多资源关闭顺序**：按声明顺序的逆序关闭
- **抑制异常**：如果 try 块和 close() 都抛出异常，close() 的异常会被抑制（addSuppressed），优先抛出 try 块的异常

### 考点六：常见异常类及场景

| 异常类 | 触发场景 |
|--------|----------|
| NullPointerException | 对象为 null 时调用方法/访问属性 |
| ArrayIndexOutOfBoundsException | 数组索引越界 |
| ClassCastException | 错误的类型转换 |
| IllegalArgumentException | 传入非法参数 |
| IllegalStateException | 对象状态不正确时调用方法 |
| ConcurrentModificationException | 迭代集合时修改集合 |
| UnsupportedOperationException | 调用不支持的操作（如修改只读集合） |
| NoSuchElementException | 集合中没有元素时调用 next() 等 |

---

## 附录：异常处理速查表

### 异常分类

```
Throwable
├── Error (不可恢复)
│   ├── OutOfMemoryError
│   ├── StackOverflowError
│   └── ...
│
└── Exception (可处理)
    ├── RuntimeException (非受检)
    │   ├── NullPointerException
    │   ├── ArrayIndexOutOfBoundsException
    │   ├── ClassCastException
    │   ├── IllegalArgumentException
    │   └── ...
    │
    └── Checked Exception (受检)
        ├── IOException
        │   ├── FileNotFoundException
        │   ├── SocketException
        │   └── ...
        ├── SQLException
        ├── ClassNotFoundException
        └── ...
```

### 处理方式选择

| 场景 | 推荐方式 |
|------|----------|
| 资源操作（文件、网络） | try-with-resources |
| 异常向上传递 | throws 声明 + 包装 |
| 业务校验失败 | 自定义业务异常 |
| 全局异常处理 | @ControllerAdvice |
| 多异常统一处理 | 多异常合并捕获 |

### 注意事项

1. **子类 catch 必须在前，父类在后**
2. **finally 中不要有 return**
3. **使用 SLF4J 参数化日志**
4. **保留异常链，不要丢失原始异常**
5. **不要用异常做业务流程控制**
6. **自定义异常要继承 RuntimeException 或 Exception**
