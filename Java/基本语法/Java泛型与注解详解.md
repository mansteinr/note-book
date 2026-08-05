# Java 泛型与注解详解

> 本文档系统讲解 Java 泛型机制与注解体系，涵盖类型擦除、通配符、自定义注解及 AOP 应用场景。

---

## 一、泛型入门

### 1.1 为什么需要泛型

在没有泛型之前，Java 集合存在以下问题：

```java
// 无泛型时代的问题
List list = new ArrayList();
list.add("字符串");
list.add(123);       // 可以添加任意类型
list.add(new Object());

// 取出来时只能得到 Object，需要强制转换
String s1 = (String) list.get(0);  // 需要手动转型
Integer i2 = (Integer) list.get(1); // 正确
String s3 = (String) list.get(2);  // ClassCastException! 运行时才报错
```

有了泛型之后：

```java
// 泛型让代码在编译期就检查类型
List<String> list = new ArrayList<>();
list.add("字符串");
// list.add(123);    // 编译错误！不允许添加非 String 类型
// list.add(1.5);    // 编译错误！

// 取出来直接是 String，无需转换
String s = list.get(0);  // 直接得到 String 类型
```

### 1.2 泛型的好处

1. **类型安全**：编译期检查，避免运行时类型转换异常
2. **代码简洁**：无需强制转换
3. **可读性强**：从声明即可看出集合存储的类型
4. **API 更灵活**：编写可重用的通用代码

---

## 二、泛型基础语法

### 2.1 泛型类

```java
// 定义泛型类
public class Box<T> {
    private T value;
    
    public Box(T value) {
        this.value = value;
    }
    
    public T getValue() {
        return value;
    }
    
    public void setValue(T value) {
        this.value = value;
    }
    
    public static void main(String[] args) {
        // 创建 String 类型的 Box
        Box<String> stringBox = new Box<>("Hello");
        String str = stringBox.getValue(); // 直接是 String
        
        // 创建 Integer 类型的 Box
        Box<Integer> intBox = new Box<>(42);
        Integer num = intBox.getValue();  // 直接是 Integer
        
        // 同一个泛型类可以实例化为不同类型
        Box<Double> doubleBox = new Box<>(3.14);
    }
}
```

### 2.2 泛型接口

```java
// 定义泛型接口
public interface Repository<T, ID> {
    T findById(ID id);
    List<T> findAll();
    T save(T entity);
    void delete(ID id);
}

// 实现泛型接口
public class UserRepository implements Repository<User, Long> {
    private Map<Long, User> storage = new HashMap<>();
    private long currentId = 1L;
    
    @Override
    public User findById(Long id) {
        return storage.get(id);
    }
    
    @Override
    public List<User> findAll() {
        return new ArrayList<>(storage.values());
    }
    
    @Override
    public User save(User user) {
        if (user.getId() == null) {
            user.setId(currentId++);
        }
        storage.put(user.getId(), user);
        return user;
    }
    
    @Override
    public void delete(Long id) {
        storage.remove(id);
    }
}
```

### 2.3 泛型方法

```java
public class GenericMethodDemo {
    
    // 泛型方法：在返回类型前声明 <T>
    public static <T> T firstElement(T[] array) {
        if (array == null || array.length == 0) {
            return null;
        }
        return array[0];
    }
    
    // 泛型方法 + 通配符
    public static void processList(List<? extends Number> list) {
        for (Number n : list) {
            System.out.println(n.doubleValue());
        }
    }
    
    // 多个类型参数
    public static <K, V> Map<K, V> mapOf(K key, V value) {
        Map<K, V> map = new HashMap<>();
        map.put(key, value);
        return map;
    }
    
    public static void main(String[] args) {
        String[] words = {"apple", "banana", "cherry"};
        String first = firstElement(words); // "apple"
        
        Map<String, Integer> map = mapOf("age", 25);
    }
}
```

---

## 三、类型边界与通配符

### 3.1 上界通配符 <? extends T>

```java
public class WildcardDemo {
    
    /**
     * 上界通配符：<? extends T>
     * 表示类型是 T 或 T 的子类
     * 可以读取 T 类型的数据，但不能添加（除了 null）
     */
    public static void processNumbers(List<? extends Number> list) {
        // 可以安全读取为 Number
        for (Number n : list) {
            System.out.println(n.doubleValue());
        }
        
        // 不能添加元素（除了 null）
        // list.add(123);     // 编译错误
        // list.add(null);    // 只有 null 可以
    }
    
    public static void main(String[] args) {
        List<Integer> intList = Arrays.asList(1, 2, 3);
        List<Double> doubleList = Arrays.asList(1.5, 2.5, 3.5);
        List<Number> numberList = new ArrayList<>();
        numberList.add(1);
        numberList.add(2.0);
        
        // 都可以传入 <? extends Number>
        processNumbers(intList);
        processNumbers(doubleList);
        processNumbers(numberList);
    }
}
```

### 3.2 下界通配符 <? super T>

```java
/**
 * 下界通配符：<? super T>
 * 表示类型是 T 或 T 的父类
 * 可以安全添加 T 类型的数据，读取时只能得到 Object
 */
public class SuperWildcardDemo {
    
    public static void addNumbers(List<? super Integer> list) {
        // 可以安全添加 Integer 及其子类
        list.add(1);
        list.add(2);
        list.add(3);
        
        // 读取时只能得到 Object
        Object obj = list.get(0);
        // Integer n = list.get(0); // 编译错误
    }
    
    public static void main(String[] args) {
        List<Integer> intList = new ArrayList<>();
        List<Number> numberList = new ArrayList<>();
        List<Object> objectList = new ArrayList<>();
        
        // 都可以接收 <? super Integer>
        addNumbers(intList);      // Integer 是 Integer
        addNumbers(numberList);   // Number 是 Integer 的父类
        addNumbers(objectList);   // Object 是 Integer 的祖父类
    }
}
```

### 3.3 通配符选择原则

| 需求 | 使用 | 说明 |
|------|------|------|
| 只读取，不写入 | `<? extends T>` | 生产者，安全读取 |
| 只写入，不读取 | `<? super T>` | 消费者，安全写入 |
| 既读又写 | `List<T>` | 明确类型 |
| 不关心类型 | `<?>` | 等价于 `<? extends Object>` |

**PECS 原则：Producer Extends, Consumer Super**

```java
public class PECSPrinciple {
    
    // 生产者（读取）：使用 extends
    public static <T> void copy(List<? extends T> src, List<? super T> dest) {
        for (T element : src) {
            dest.add(element);
        }
    }
    
    // 典型应用：Collections.copy()
    // public static <T> void copy(List<? super T> dest, List<? extends T> src)
}
```

### 3.4 类型变量绑定

```java
public class BoundedTypeParameter {
    
    /**
     * 类型绑定：<T extends T>
     * 限定类型参数必须是某个类的子类
     */
    public static <T extends Number> double sum(List<T> list) {
        double total = 0;
        for (T n : list) {
            total += n.doubleValue(); // 可以安全调用 Number 的方法
        }
        return total;
    }
    
    /**
     * 多类型绑定：<T extends A & B>
     * T 必须同时满足 A 和 B
     */
    public static <T extends Number & Comparable<T>> T max(T a, T b) {
        return a.compareTo(b) > 0 ? a : b;
    }
    
    public static void main(String[] args) {
        List<Integer> intList = Arrays.asList(1, 2, 3);
        double intSum = sum(intList); // 6.0
        
        List<Double> doubleList = Arrays.asList(1.5, 2.5, 3.5);
        double doubleSum = sum(doubleList); // 7.5
    }
}
```

---

## 四、类型擦除

### 4.1 什么是类型擦除

Java 泛型是编译期特性，编译后类型参数会被擦除，替换为原始类型（Raw Type）。

```java
// 编译前
List<String> strList = new ArrayList<>();
List<Integer> intList = new ArrayList<>();

// 编译后（类型擦除）
List strList = new ArrayList();  // 变成原始类型 List
List intList = new ArrayList();  // 变成原始类型 List
```

### 4.2 擦除规则

| 泛型类型 | 擦除后 |
|---------|--------|
| `List<T>` | `List` |
| `List<String>` | `List` |
| `Map<K, V>` | `Map` |
| `<T extends Number>` | `Number` |
| `<T extends Comparable>` | `Comparable` |
| `<? extends Number>` | `Number` |
| `<? super Integer>` | `Object` |

### 4.3 类型擦除的影响

**无法在运行时获取泛型信息：**

```java
public class ErasureEffects {
    
    public static void main(String[] args) {
        // 1. 无法通过反射获取泛型类型
        List<String> strList = new ArrayList<>();
        List<Integer> intList = new ArrayList<>();
        
        // 运行时两者的 Class 对象相同
        System.out.println(strList.getClass() == intList.getClass()); // true
        
        // 2. 不能直接创建泛型数组
        // List<String>[] arr = new ArrayList<String>[10]; // 编译错误
        // 解决方案：
        @SuppressWarnings("unchecked")
        List<String>[] arr = (List<String>[]) new ArrayList[10];
        
        // 3. 不能以泛型类型作为方法参数重载
        // void process(List<String> list)
        // void process(List<Integer> list)  // 编译错误！签名擦除后相同
        
        // 4. 不能在泛型中使用 instanceof
        // if (obj instanceof List<String>) // 编译错误
        if (obj instanceof List) { // 只能检查原始类型
            List<?> list = (List<?>) obj;
        }
    }
}
```

**桥接方法（Bridge Method）：**

```java
/**
 * 类型擦除后，子类会生成桥接方法以保持多态
 */
public class BridgeMethodDemo {
    
    // 泛型父类
    public static class Base<T> {
        public T getValue() {
            return null;
        }
        public void setValue(T value) {
        }
    }
    
    // 特定类型子类
    public static class StringChild extends Base<String> {
        @Override
        public String getValue() {
            return "Hello";
        }
        // 编译后会生成桥接方法：
        // public Object getValue() { return getValue(); }
        // 这样多态调用才能正确
    }
    
    // 实际案例：HashMap
    // 源码中：Node<K,V> implements Map.Entry<K,V>
    // 编译后会生成桥接方法
}
```

### 4.4 绕过类型擦除

```java
public class BypassErasure {
    
    /**
     * 通过反射获取泛型信息
     * 这是框架（如 Spring, MyBatis）常用的技巧
     */
    
    // 方式一：类的成员变量
    public static void getFieldGenericType() throws Exception {
        class UserService {
            private List<String> userNames;
        }
        
        Field field = UserService.class.getDeclaredField("userNames");
        Type genericType = field.getGenericType();
        
        if (genericType instanceof ParameterizedType) {
            ParameterizedType pt = (ParameterizedType) genericType;
            Type[] typeArgs = pt.getActualTypeArguments();
            System.out.println("元素类型: " + typeArgs[0]); // class java.lang.String
        }
    }
    
    // 方式二：方法返回值
    public static void getMethodReturnGeneric() throws Exception {
        class UserService {
            public List<String> getNames() {
                return null;
            }
        }
        
        Method method = UserService.class.getMethod("getNames");
        Type returnType = method.getGenericReturnType();
        
        if (returnType instanceof ParameterizedType) {
            ParameterizedType pt = (ParameterizedType) returnType;
            System.out.println("返回元素类型: " + pt.getActualTypeArguments()[0]);
        }
    }
    
    // 方式三：继承时保留泛型信息（框架常用）
    public static abstract class BaseDao<T> {
        private Class<T> entityClass;
        
        protected BaseDao() {
            // 从子类的泛型中获取类型信息
            Type type = getClass().getGenericSuperclass();
            if (type instanceof ParameterizedType) {
                ParameterizedType pt = (ParameterizedType) type;
                this.entityClass = (Class<T>) pt.getActualTypeArguments()[0];
            }
        }
        
        public Class<T> getEntityClass() {
            return entityClass;
        }
    }
    
    // 子类实例化时确定类型
    public static class UserDao extends BaseDao<User> {
        // entityClass 会自动被设置为 User.class
    }
    
    public static void main(String[] args) throws Exception {
        getFieldGenericType();
        getMethodReturnGeneric();
        
        UserDao userDao = new UserDao();
        System.out.println("实体类: " + userDao.getEntityClass()); // class User
    }
    
    // 辅助类
    static class User {
        private String name;
    }
}
```

---

## 五、注解基础

### 5.1 什么是注解

注解（Annotation）是一种元数据机制，可以为代码附加额外信息，供编译器、框架或运行时处理。

```java
// 常见注解示例
@Override           // 标记方法重写
@Deprecated         // 标记过时方法
@SuppressWarnings   // 抑制编译器警告
@Test               // 标记测试方法
@Service            // 标记 Spring 服务类
@RequestMapping      // 映射请求路径
```

### 5.2 元注解

元注解是用于修饰注解的注解。

```java
// @Target：指定注解可以修饰的程序元素
// ElementType.TYPE       类、接口、枚举
// ElementType.METHOD     方法
// ElementType.FIELD      字段
// ElementType.PARAMETER  参数
// ElementType.CONSTRUCTOR 构造方法
// ElementType.LOCAL_VARIABLE 局部变量
// ElementType.PACKAGE    包

@Target({ElementType.TYPE, ElementType.METHOD})

// @Retention：指定注解的保留策略
// RetentionPolicy.SOURCE   源码级（编译后丢弃）
// RetentionPolicy.CLASS    字节码级（运行时不保留）
// RetentionPolicy.RUNTIME  运行时级（可通过反射获取）

@Retention(RetentionPolicy.RUNTIME)

// @Documented：生成 JavaDoc 时包含注解
@Documented

// @Inherited：子类自动继承父类注解
@Inherited

// @Repeatable：注解可以重复使用（Java 8+）
@Repeatable(MyAnnotations.class)
```

### 5.3 常见内置注解

```java
public class BuiltInAnnotations {
    
    // @Override：标记方法重写
    @Override
    public String toString() {
        return "Custom toString";
    }
    
    // @Deprecated：标记过时 API
    @Deprecated
    public void oldMethod() {
        // 不推荐使用
    }
    
    // @SuppressWarnings：抑制警告
    @SuppressWarnings("unchecked")
    public void unsafeMethod() {
        List list = new ArrayList();
        list.add("item"); // 会有 unchecked 警告
    }
    
    // @FunctionalInterface：标记函数式接口（Java 8+）
    @FunctionalInterface
    public interface MyFunction<T, R> {
        R apply(T t);
    }
    
    // @SafeVarargs：安全可变参数（Java 7+）
    @SafeVarargs
    public final void processList(List<String>... lists) {
        // 避免堆污染警告
    }
}
```

---

## 六、自定义注解

### 6.1 创建自定义注解

```java
/**
 * 自定义注解：记录方法执行时间
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface Timed {
    // 注解的属性（可选）
    String description() default "";
    long warnThreshold() default 1000; // 警告阈值（毫秒）
}

/**
 * 自定义注解：需要登录
 */
@Target({ElementType.TYPE, ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
public @interface RequireLogin {
    boolean required() default true;
    String[] roles() default {}; // 需要的角色
}
```

### 6.2 使用自定义注解

```java
public class CustomAnnotationUsage {
    
    @Timed(description = "用户登录", warnThreshold = 500)
    @RequireLogin(roles = {"admin", "user"})
    public void login(String username, String password) {
        // 业务逻辑
    }
    
    @Timed(description = "获取用户列表")
    public List<User> getUsers() {
        // 业务逻辑
        return new ArrayList<>();
    }
}
```

### 6.3 运行时读取注解

```java
/**
 * 注解处理器：通过反射读取注解信息
 */
public class AnnotationProcessor {
    
    // 处理 @Timed 注解
    public static void processTimedAnnotation(Object target) {
        Class<?> clazz = target.getClass();
        
        // 获取类上的注解
        Timed classTimed = clazz.getAnnotation(Timed.class);
        if (classTimed != null) {
            System.out.println("类注解: " + classTimed.description());
        }
        
        // 获取方法上的注解
        for (Method method : clazz.getDeclaredMethods()) {
            Timed timed = method.getAnnotation(Timed.class);
            if (timed != null) {
                System.out.println("方法: " + method.getName());
                System.out.println("描述: " + timed.description());
                System.out.println("警告阈值: " + timed.warnThreshold() + "ms");
            }
        }
    }
    
    // 动态代理示例：实现 @Timed 的计时功能
    public static <T> T createProxy(T target) {
        return (T) Proxy.newProxyInstance(
            target.getClass().getClassLoader(),
            target.getClass().getInterfaces(),
            (proxy, method, args) -> {
                // 检查方法是否有 @Timed 注解
                Timed timed = method.getAnnotation(Timed.class);
                if (timed != null) {
                    long start = System.currentTimeMillis();
                    Object result = method.invoke(target, args);
                    long elapsed = System.currentTimeMillis() - start;
                    
                    if (elapsed > timed.warnThreshold()) {
                        System.out.println("⚠️ 方法执行超时: " + method.getName() 
                            + " 耗时 " + elapsed + "ms");
                    }
                    return result;
                }
                
                return method.invoke(target, args);
            }
        );
    }
}
```

### 6.4 注解的实际应用

```java
/**
 * 自定义注解实现简单的 MVC 框架
 */

// 路由注解
@Target({ElementType.TYPE, ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
public @interface RequestMapping {
    String value() default "";
    String method() default "GET";
}

// 控制器注解
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
public @interface Controller {
    String value() default "";
}

// 参数注解
@Target(ElementType.PARAMETER)
@Retention(RetentionPolicy.RUNTIME)
public @interface RequestParam {
    String value() default "";
    boolean required() default true;
    String defaultValue() default "";
}

// 使用示例
@Controller
@RequestMapping("/api/users")
public class UserController {
    
    @RequestMapping(value = "/{id}", method = "GET")
    public String getUser(@RequestParam("id") Long id) {
        return "User: " + id;
    }
    
    @RequestMapping(method = "POST")
    public String createUser(@RequestParam("name") String name) {
        return "Created: " + name;
    }
}

// 框架核心：扫描注解并注册路由
public class SimpleFramework {
    
    private Map<String, Method> routes = new HashMap<>();
    
    // 扫描控制器
    public void scanControllers(String... basePackages) {
        for (String pkg : basePackages) {
            // 扫描包下的所有类
            // 查找 @Controller 注解的类
            // 查找 @RequestMapping 注解的方法
            // 注册路由
        }
    }
    
    // 注册路由
    private void registerRoute(Class<?> controllerClass, Method method) {
        StringBuilder path = new StringBuilder();
        
        // 获取类级别的路径
        Controller ctrlAnno = controllerClass.getAnnotation(Controller.class);
        if (ctrlAnno != null && !ctrlAnno.value().isEmpty()) {
            path.append(ctrlAnno.value());
        }
        
        // 获取方法级别的路径
        RequestMapping methodAnno = method.getAnnotation(RequestMapping.class);
        if (methodAnno != null) {
            path.append(methodAnno.value());
            String httpMethod = methodAnno.method();
            
            String routeKey = httpMethod + ":" + path;
            routes.put(routeKey, method);
        }
    }
    
    // 处理请求
    public String handleRequest(String httpMethod, String path, Map<String, String> params) {
        String routeKey = httpMethod + ":" + path;
        Method method = routes.get(routeKey);
        
        if (method != null) {
            try {
                // 获取参数信息
                Parameter[] parameters = method.getParameters();
                Object[] args = new Object[parameters.length];
                
                for (int i = 0; i < parameters.length; i++) {
                    RequestParam paramAnno = parameters[i].getAnnotation(RequestParam.class);
                    if (paramAnno != null) {
                        String paramName = paramAnno.value();
                        String value = params.get(paramName);
                        // 类型转换
                        args[i] = convertType(value, parameters[i].getType());
                    }
                }
                
                // 调用方法
                method.setAccessible(true);
                Object result = method.invoke(null, args);
                return (String) result;
                
            } catch (Exception e) {
                return "Error: " + e.getMessage();
            }
        }
        
        return "404 Not Found";
    }
    
    private Object convertType(String value, Class<?> type) {
        if (type == Long.class || type == long.class) {
            return Long.parseLong(value);
        } else if (type == Integer.class || type == int.class) {
            return Integer.parseInt(value);
        }
        return value;
    }
}
```

---

## 七、面试高频考点

### 泛型相关

**Q1: 什么是类型擦除？**

A: 类型擦除是 Java 泛型的实现机制，编译后将泛型类型参数替换为原始类型。`<T>` 变为 `Object`，`<T extends Number>` 变为 `Number`。这导致无法在运行时获取泛型信息。

**Q2: ArrayList<String> 和 ArrayList<Integer> 是同一个类型吗？**

A: 是的。由于类型擦除，它们编译后都是 `ArrayList`，运行时 `getClass()` 返回相同的 Class 对象。但编译期是不同的类型。

**Q3: 能否用泛型类型做方法重载？**

A: 不能。例如 `void process(List<String>)` 和 `void process(List<Integer>)` 会编译错误，因为类型擦除后方法签名相同。

**Q4: <? extends T> 和 <? super T> 的区别？**

A:
- `<? extends T>` 可以安全读取为 T 类型，但不能添加
- `<? super T>` 可以安全添加 T 类型，但读取只能得到 Object
- PECS 原则：Producer Extends（生产者用 extends），Consumer Super（消费者用 super）

**Q5: 如何绕过类型擦除获取泛型信息？**

A: 通过反射 `getGenericType()` 方法，可以在成员变量、方法返回值等地方获取泛型信息。这是框架设计的重要技巧。

### 注解相关

**Q6: 注解的三种保留策略是什么？**

A:
- `SOURCE`：仅在源码中存在，编译后丢弃（如 `@Override`）
- `CLASS`：编译到字节码，运行时不保留
- `RUNTIME`：运行时保留，可通过反射获取（框架常用）

**Q7: 如何创建自定义注解？**

A:
1. 使用 `@interface` 关键字声明
2. 使用 `@Target` 指定适用范围
3. 使用 `@Retention(RetentionPolicy.RUNTIME)` 使其运行时可用
4. 定义注解属性（可选）
5. 通过反射在运行时读取

**Q8: 注解和 XML 配置相比有什么优势？**

A:
- 类型安全：编译期检查
- 代码简洁：与代码放在一起，便于阅读
- 重构友好：重命名时注解自动更新
- 功能强大：可以通过反射实现复杂逻辑

**Q9: Spring 常用注解有哪些？**

A:
- `@Component` / `@Service` / `@Repository` / `@Controller`：声明 Bean
- `@Autowired` / `@Resource`：依赖注入
- `@Configuration` / `@Bean`：配置类
- `@RequestMapping` / `@GetMapping` / `@PostMapping`：Web 路由
- `@Transactional`：事务管理
- `@Aspect` / `@Before` / `@After`：AOP

**Q10: 如何实现注解驱动的功能？**

A:
1. 创建自定义注解（`@Target`, `@Retention(RUNTIME)`）
2. 在目标元素上使用注解
3. 通过反射扫描带有注解的元素
4. 读取注解属性
5. 根据注解信息执行相应逻辑
6. 可结合动态代理实现 AOP 功能
