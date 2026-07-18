# Java 基本语法学习指南

## 目录

- [一、Java 语言概述](#一java-语言概述)
- [二、数据类型](#二数据类型)
- [三、变量与常量](#三变量与常量)
- [四、运算符](#四运算符)
- [五、控制流语句](#五控制流语句)
- [六、数组](#六数组)
- [七、方法](#七方法)
- [八、面向对象基础](#八面向对象基础)
- [九、字符串处理](#九字符串处理)
- [十、异常处理](#十异常处理)
- [十一、线程处理](#十一线程处理)
- [附录：Java 编码规范](#附录java-编码规范)

---

## 一、Java 语言概述

### 1.1 Java 的特点

| 特点 | 说明 |
|-----|------|
| **跨平台** | "一次编写，到处运行"，通过 JVM 实现 |
| **面向对象** | 一切皆对象，支持封装、继承、多态 |
| **自动内存管理** | 垃圾回收机制（GC）自动回收不再使用的对象 |
| **强类型语言** | 变量必须先声明类型，编译时进行类型检查 |
| **多线程支持** | 内建多线程支持，适合并发编程 |

### 1.2 第一个 Java 程序

```java
// 这是 Java 程序的入口：main 方法
public class HelloWorld {
    public static void main(String[] args) {
        // 输出到控制台
        System.out.println("Hello, World!");
        System.out.println("欢迎来到 Java 的世界！");
    }
}
```

**编译和运行：**

```bash
# 编译：生成 .class 字节码文件
javac HelloWorld.java

# 运行：通过 JVM 执行字节码
java HelloWorld
```

**运行结果：**

```
Hello, World!
欢迎来到 Java 的世界！
```

### 1.3 Java 程序的基本结构

```java
// 1. 包声明（可选）
package com.example;

// 2. 导入语句（可选）
import java.util.Scanner;

// 3. 类声明（必须）
public class MyClass {
    
    // 4. 类变量（静态变量）
    static int classVar = 0;
    
    // 5. 实例变量
    private String name;
    
    // 6. 构造方法
    public MyClass() {
        this.name = "默认名称";
    }
    
    // 7. 方法
    public void sayHello() {
        System.out.println("Hello, " + name);
    }
    
    // 8. main 方法（程序入口）
    public static void main(String[] args) {
        MyClass obj = new MyClass();
        obj.sayHello();
    }
}
```

---

## 二、数据类型

Java 的数据类型分为两大类：**基本数据类型**（8种）和 **引用数据类型**。

### 2.1 基本数据类型

| 类型 | 关键字 | 字节数 | 取值范围 | 默认值 | 示例 |
|-----|-------|-------|---------|-------|------|
| 字节型 | `byte` | 1 | -128 ~ 127 | 0 | `byte b = 127;` |
| 短整型 | `short` | 2 | -32768 ~ 32767 | 0 | `short s = 32767;` |
| 整型 | `int` | 4 | -2^31 ~ 2^31-1 | 0 | `int i = 100;` |
| 长整型 | `long` | 8 | -2^63 ~ 2^63-1 | 0L | `long l = 100L;` |
| 单精度浮点 | `float` | 4 | ±3.4E38 | 0.0f | `float f = 3.14f;` |
| 双精度浮点 | `double` | 8 | ±1.8E308 | 0.0d | `double d = 3.14;` |
| 字符型 | `char` | 2 | 0 ~ 65535（Unicode） | '\u0000' | `char c = 'A';` |
| 布尔型 | `boolean` | - | true / false | false | `boolean b = true;` |

```java
public class DataTypes {
    public static void main(String[] args) {
        // 整数类型
        byte byteVal = 127;
        short shortVal = 32767;
        int intVal = 2147483647;
        long longVal = 9223372036854775807L;  // long 类型需要加 L 后缀
        
        // 浮点类型
        float floatVal = 3.14f;      // float 类型需要加 f 后缀
        double doubleVal = 3.14159;  // double 是默认浮点类型
        
        // 字符类型
        char charVal = 'A';          // 单个字符，用单引号
        char unicodeChar = '\u4e2d'; // Unicode 编码：'中'
        
        // 布尔类型
        boolean boolVal = true;      // 只有 true 和 false
        
        // 输出各类型信息
        System.out.println("byte: " + byteVal + "，占用 " + Byte.SIZE/8 + " 字节");
        System.out.println("short: " + shortVal + "，占用 " + Short.SIZE/8 + " 字节");
        System.out.println("int: " + intVal + "，占用 " + Integer.SIZE/8 + " 字节");
        System.out.println("long: " + longVal + "，占用 " + Long.SIZE/8 + " 字节");
        System.out.println("float: " + floatVal + "，占用 " + Float.SIZE/8 + " 字节");
        System.out.println("double: " + doubleVal + "，占用 " + Double.SIZE/8 + " 字节");
        System.out.println("char: " + charVal + "，占用 " + Character.SIZE/8 + " 字节");
        System.out.println("boolean: " + boolVal);
        System.out.println("Unicode字符: " + unicodeChar);
    }
}
```

### 2.2 引用数据类型

引用数据类型包括：**类（Class）**、**接口（Interface）**、**数组（Array）**、**字符串（String）** 等。

```java
public class ReferenceTypes {
    public static void main(String[] args) {
        // 字符串（最常用的引用类型）
        String str = "Hello, Java";
        
        // 数组
        int[] numbers = {1, 2, 3, 4, 5};
        
        // 对象
        Object obj = new Object();
        
        // 包装类（基本类型对应的引用类型）
        Integer intObj = 100;       // int 的包装类
        Double doubleObj = 3.14;    // double 的包装类
        Boolean boolObj = true;     // boolean 的包装类
        
        System.out.println("String: " + str);
        System.out.println("数组长度: " + numbers.length);
        System.out.println("Integer: " + intObj);
        System.out.println("Double: " + doubleObj);
        System.out.println("Boolean: " + boolObj);
    }
}
```

### 2.3 类型转换

```java
public class TypeConversion {
    public static void main(String[] args) {
        // ====== 自动类型转换（小类型 → 大类型）======
        int intVal = 100;
        long longVal = intVal;       // int → long，自动转换
        double doubleVal = longVal;  // long → double，自动转换
        
        System.out.println("自动转换：int → long → double");
        System.out.println("int: " + intVal);
        System.out.println("long: " + longVal);
        System.out.println("double: " + doubleVal);
        
        // ====== 强制类型转换（大类型 → 小类型）======
        double pi = 3.14159;
        int intPi = (int) pi;  // double → int，需要强制转换，会丢失小数部分
        
        System.out.println("\n强制转换：double → int");
        System.out.println("double: " + pi);
        System.out.println("int: " + intPi);  // 结果为 3，小数部分被截断
        
        // ====== 注意事项 ======
        // 1. 浮点转整数会丢失精度
        double d = 9.999;
        int i = (int) d;  // 结果为 9，不是 10
        
        // 2. 大整数转小类型可能溢出
        int bigNum = 130;
        byte smallNum = (byte) bigNum;  // 结果为 -126（溢出）
        
        System.out.println("\n注意事项：");
        System.out.println("9.999 强制转 int: " + i);
        System.out.println("130 强制转 byte: " + smallNum);
    }
}
```

---

## 三、变量与常量

### 3.1 变量声明与初始化

```java
public class VariableDemo {
    public static void main(String[] args) {
        // 方式一：先声明后赋值
        int age;
        age = 25;
        
        // 方式二：声明同时赋值（推荐）
        String name = "张三";
        
        // 方式三：同时声明多个同类型变量
        int x = 10, y = 20, z = 30;
        
        System.out.println("age = " + age);
        System.out.println("name = " + name);
        System.out.println("x = " + x + ", y = " + y + ", z = " + z);
    }
}
```

### 3.2 变量作用域

```java
public class VariableScope {
    // 类变量（静态变量）：整个类可见
    static int classVar = 100;
    
    // 实例变量：对象级别可见
    int instanceVar = 200;
    
    public void method() {
        // 局部变量：方法内可见
        int localVar = 300;
        
        {
            // 代码块变量：代码块内可见
            int blockVar = 400;
            System.out.println("代码块内: blockVar = " + blockVar);
        }
        // System.out.println(blockVar);  // 编译错误：blockVar 超出作用域
        
        System.out.println("方法内: localVar = " + localVar);
        System.out.println("实例变量: instanceVar = " + instanceVar);
        System.out.println("类变量: classVar = " + classVar);
    }
    
    public static void main(String[] args) {
        VariableScope obj = new VariableScope();
        obj.method();
        
        System.out.println("main方法中访问类变量: classVar = " + VariableScope.classVar);
    }
}
```

### 3.3 常量

```java
public class ConstantDemo {
    public static void main(String[] args) {
        // 使用 final 关键字定义常量
        final double PI = 3.14159265358979;
        final String APP_VERSION = "1.0.0";
        final int MAX_USERS = 1000;
        
        System.out.println("PI = " + PI);
        System.out.println("版本: " + APP_VERSION);
        System.out.println("最大用户数: " + MAX_USERS);
        
        // PI = 3.14;  // 编译错误：常量不能重新赋值
        
        // 类常量：static final 修饰
        System.out.println("\n类常量示例：");
        System.out.println("Math.PI = " + Math.PI);
        System.out.println("Math.E = " + Math.E);
    }
}
```

### 3.4 命名规范

| 类型 | 命名规则 | 示例 |
|-----|---------|------|
| 类名 | 大驼峰（PascalCase） | `StudentInfo`、`UserService` |
| 方法名 | 小驼峰（camelCase） | `getUserName()`、`calculateTotal()` |
| 变量名 | 小驼峰（camelCase） | `userName`、`orderCount` |
| 常量名 | 全大写 + 下划线 | `MAX_SIZE`、`DEFAULT_TIMEOUT` |
| 包名 | 全小写 | `com.example.service` |

---

## 四、运算符

### 4.1 算术运算符

```java
public class ArithmeticOperators {
    public static void main(String[] args) {
        int a = 17, b = 5;
        
        System.out.println("a = " + a + ", b = " + b);
        System.out.println("========================");
        
        // 基本算术运算
        System.out.println("a + b = " + (a + b));   // 加法：22
        System.out.println("a - b = " + (a - b));   // 减法：12
        System.out.println("a * b = " + (a * b));   // 乘法：85
        System.out.println("a / b = " + (a / b));   // 整数除法：3（不是 3.4）
        System.out.println("a % b = " + (a % b));   // 取余：2
        
        // 整数除法 vs 浮点除法
        System.out.println("\n整数除法 vs 浮点除法：");
        System.out.println("17 / 5 = " + (17 / 5));           // 3（整数除法）
        System.out.println("17.0 / 5 = " + (17.0 / 5));       // 3.4（浮点除法）
        System.out.println("17 / 5.0 = " + (17 / 5.0));       // 3.4（浮点除法）
        
        // 自增自减运算符
        int x = 10;
        System.out.println("\n自增自减运算符：");
        System.out.println("x = " + x);
        System.out.println("x++ = " + (x++));  // 先使用再加1，输出10
        System.out.println("x = " + x);         // x 现在是 11
        System.out.println("++x = " + (++x));  // 先加1再使用，输出12
        System.out.println("x = " + x);         // x 现在是 12
        System.out.println("x-- = " + (x--));  // 先使用再减1，输出12
        System.out.println("x = " + x);         // x 现在是 11
        System.out.println("--x = " + (--x));  // 先减1再使用，输出10
    }
}
```

### 4.2 关系运算符

```java
public class RelationalOperators {
    public static void main(String[] args) {
        int a = 10, b = 20;
        
        System.out.println("a = " + a + ", b = " + b);
        System.out.println("========================");
        
        // 关系运算符返回 boolean 值
        System.out.println("a == b: " + (a == b));   // 等于：false
        System.out.println("a != b: " + (a != b));   // 不等于：true
        System.out.println("a > b: " + (a > b));     // 大于：false
        System.out.println("a < b: " + (a < b));     // 小于：true
        System.out.println("a >= b: " + (a >= b));   // 大于等于：false
        System.out.println("a <= b: " + (a <= b));   // 小于等于：true
        
        // 注意：== 比较基本类型是比值，比较引用类型是比地址
        String s1 = new String("hello");
        String s2 = new String("hello");
        System.out.println("\n字符串比较：");
        System.out.println("s1 == s2: " + (s1 == s2));         // false（地址不同）
        System.out.println("s1.equals(s2): " + s1.equals(s2)); // true（内容相同）
    }
}
```

### 4.3 逻辑运算符

```java
public class LogicalOperators {
    public static void main(String[] args) {
        boolean a = true, b = false;
        
        System.out.println("a = " + a + ", b = " + b);
        System.out.println("========================");
        
        // 基本逻辑运算
        System.out.println("a && b: " + (a && b));   // 逻辑与（短路与）：false
        System.out.println("a || b: " + (a || b));   // 逻辑或（短路或）：true
        System.out.println("!a: " + (!a));           // 逻辑非：false
        
        // 短路与 vs 非短路与
        System.out.println("\n短路与（&&）vs 非短路与（&）：");
        int x = 5, y = 10;
        
        // && 短路：左边为 false 时不执行右边
        boolean result1 = (x > 10) && (++y > 10);
        System.out.println("使用 &&: result1 = " + result1 + ", y = " + y);  // y 仍为 10
        
        // & 不短路：无论左边结果如何都执行右边
        boolean result2 = (x > 10) & (++y > 10);
        System.out.println("使用 &: result2 = " + result2 + ", y = " + y);   // y 变为 11
        
        // 实际应用：安全的空值检查
        System.out.println("\n实际应用 - 安全的空值检查：");
        String str = null;
        // 使用 && 短路，str 为 null 时不会调用 length()，避免 NullPointerException
        if (str != null && str.length() > 0) {
            System.out.println("字符串非空");
        } else {
            System.out.println("字符串为空或 null");
        }
    }
}
```

### 4.4 赋值运算符

```java
public class AssignmentOperators {
    public static void main(String[] args) {
        int a = 10;
        
        System.out.println("初始值: a = " + a);
        System.out.println("========================");
        
        // 复合赋值运算符
        a += 5;    // 等价于 a = a + 5
        System.out.println("a += 5 → a = " + a);   // 15
        
        a -= 3;    // 等价于 a = a - 3
        System.out.println("a -= 3 → a = " + a);   // 12
        
        a *= 2;    // 等价于 a = a * 2
        System.out.println("a *= 2 → a = " + a);   // 24
        
        a /= 4;    // 等价于 a = a / 4
        System.out.println("a /= 4 → a = " + a);   // 6
        
        a %= 4;    // 等价于 a = a % 4
        System.out.println("a %= 4 → a = " + a);   // 2
        
        // 三元运算符（条件运算符）
        System.out.println("\n三元运算符：");
        int x = 10, y = 20;
        int max = (x > y) ? x : y;  // 如果 x > y 则取 x，否则取 y
        System.out.println("x = " + x + ", y = " + y);
        System.out.println("max = " + max);  // 20
        
        // 三元运算符替代 if-else
        int age = 20;
        String status = (age >= 18) ? "成年" : "未成年";
        System.out.println("年龄: " + age + ", 状态: " + status);
    }
}
```

### 4.5 位运算符

```java
public class BitwiseOperators {
    public static void main(String[] args) {
        int a = 12;   // 二进制: 0000 1100
        int b = 10;   // 二进制: 0000 1010
        
        System.out.println("a = " + a + " (二进制: " + Integer.toBinaryString(a) + ")");
        System.out.println("b = " + b + " (二进制: " + Integer.toBinaryString(b) + ")");
        System.out.println("========================");
        
        System.out.println("a & b  = " + (a & b));   // 按位与: 0000 1000 = 8
        System.out.println("a | b  = " + (a | b));   // 按位或: 0000 1110 = 14
        System.out.println("a ^ b  = " + (a ^ b));   // 按位异或: 0000 0110 = 6
        System.out.println("~a     = " + (~a));       // 按位取反: 1111 0011 = -13
        System.out.println("a << 2 = " + (a << 2));  // 左移2位: 0011 0000 = 48
        System.out.println("a >> 2 = " + (a >> 2));  // 右移2位: 0000 0011 = 3
        
        // 实际应用：判断奇偶
        System.out.println("\n实际应用 - 判断奇偶：");
        int num = 7;
        if ((num & 1) == 0) {
            System.out.println(num + " 是偶数");
        } else {
            System.out.println(num + " 是奇数");  // 输出这行
        }
    }
}
```

### 4.6 运算符优先级

| 优先级 | 运算符 | 结合性 |
|-------|--------|-------|
| 1（最高） | `()` `[]` `.` | 左到右 |
| 2 | `!` `~` `++` `--` `+`(正) `-`(负) | 右到左 |
| 3 | `*` `/` `%` | 左到右 |
| 4 | `+` `-` | 左到右 |
| 5 | `<<` `>>` `>>>` | 左到右 |
| 6 | `<` `<=` `>` `>=` | 左到右 |
| 7 | `==` `!=` | 左到右 |
| 8 | `&` | 左到右 |
| 9 | `^` | 左到右 |
| 10 | `\|` | 左到右 |
| 11 | `&&` | 左到右 |
| 12 | `\|\|` | 左到右 |
| 13 | `?:` | 右到左 |
| 14（最低） | `=` `+=` `-=` 等 | 右到左 |

---

## 五、控制流语句

### 5.1 条件语句

#### if-else 语句

```java
public class IfElseDemo {
    public static void main(String[] args) {
        int score = 85;
        
        // 简单 if
        if (score >= 60) {
            System.out.println("恭喜，考试及格了！");
        }
        
        // if-else
        if (score >= 60) {
            System.out.println("及格");
        } else {
            System.out.println("不及格");
        }
        
        // if-else if-else（多条件判断）
        String grade;
        if (score >= 90) {
            grade = "A（优秀）";
        } else if (score >= 80) {
            grade = "B（良好）";
        } else if (score >= 70) {
            grade = "C（中等）";
        } else if (score >= 60) {
            grade = "D（及格）";
        } else {
            grade = "F（不及格）";
        }
        
        System.out.println("分数: " + score + ", 等级: " + grade);
        
        // 嵌套 if
        int age = 25;
        boolean hasLicense = true;
        
        if (age >= 18) {
            if (hasLicense) {
                System.out.println("可以开车");
            } else {
                System.out.println("需要先考驾照");
            }
        } else {
            System.out.println("未成年，不能开车");
        }
    }
}
```

#### switch 语句

```java
public class SwitchDemo {
    public static void main(String[] args) {
        // 基本 switch（支持 int、char、String、枚举）
        int dayOfWeek = 3;
        
        switch (dayOfWeek) {
            case 1:
                System.out.println("星期一");
                break;
            case 2:
                System.out.println("星期二");
                break;
            case 3:
                System.out.println("星期三");
                break;
            case 4:
                System.out.println("星期四");
                break;
            case 5:
                System.out.println("星期五");
                break;
            case 6:
            case 7:
                System.out.println("周末");
                break;
            default:
                System.out.println("无效的日期");
                break;
        }
        
        // switch 支持 String（Java 7+）
        String season = "spring";
        switch (season.toLowerCase()) {
            case "spring":
                System.out.println("春天 - 万物复苏");
                break;
            case "summer":
                System.out.println("夏天 - 骄阳似火");
                break;
            case "autumn":
            case "fall":
                System.out.println("秋天 - 硕果累累");
                break;
            case "winter":
                System.out.println("冬天 - 白雪皑皑");
                break;
            default:
                System.out.println("未知季节");
        }
        
        // switch 表达式（Java 14+，使用 -> 语法）
        // int numLetters = switch (grade) {
        //     case "A" -> 4;
        //     case "B" -> 3;
        //     case "C" -> 2;
        //     default -> 1;
        // };
        
        // 实际应用：根据月份判断季节
        int month = 8;
        switch (month) {
            case 3: case 4: case 5:
                System.out.println(month + "月是春季");
                break;
            case 6: case 7: case 8:
                System.out.println(month + "月是夏季");
                break;
            case 9: case 10: case 11:
                System.out.println(month + "月是秋季");
                break;
            case 12: case 1: case 2:
                System.out.println(month + "月是冬季");
                break;
            default:
                System.out.println("无效的月份");
        }
    }
}
```

### 5.2 循环语句

#### for 循环

```java
public class ForLoopDemo {
    public static void main(String[] args) {
        // 基本 for 循环
        System.out.println("=== 基本 for 循环 ===");
        for (int i = 1; i <= 5; i++) {
            System.out.println("第 " + i + " 次循环");
        }
        
        // 求 1 到 100 的和
        int sum = 0;
        for (int i = 1; i <= 100; i++) {
            sum += i;
        }
        System.out.println("\n1 到 100 的和 = " + sum);  // 5050
        
        // 遍历数组
        System.out.println("\n=== 遍历数组 ===");
        int[] numbers = {10, 20, 30, 40, 50};
        for (int i = 0; i < numbers.length; i++) {
            System.out.println("numbers[" + i + "] = " + numbers[i]);
        }
        
        // 增强 for 循环（for-each）
        System.out.println("\n=== 增强 for 循环 ===");
        for (int num : numbers) {
            System.out.println("num = " + num);
        }
        
        // 嵌套循环：九九乘法表
        System.out.println("\n=== 九九乘法表 ===");
        for (int i = 1; i <= 9; i++) {
            for (int j = 1; j <= i; j++) {
                System.out.print(j + "×" + i + "=" + (i * j) + "\t");
            }
            System.out.println();  // 换行
        }
        
        // 打印图形：直角三角形
        System.out.println("\n=== 直角三角形 ===");
        for (int i = 1; i <= 5; i++) {
            for (int j = 1; j <= i; j++) {
                System.out.print("* ");
            }
            System.out.println();
        }
    }
}
```

#### while 循环

```java
public class WhileLoopDemo {
    public static void main(String[] args) {
        // 基本 while 循环
        System.out.println("=== while 循环 ===");
        int count = 1;
        while (count <= 5) {
            System.out.println("count = " + count);
            count++;
        }
        
        // while 循环求和
        int sum = 0;
        int n = 1;
        while (n <= 100) {
            sum += n;
            n++;
        }
        System.out.println("\n1 到 100 的和 = " + sum);
        
        // 猜数字游戏
        System.out.println("\n=== 猜数字游戏 ===");
        int target = 42;
        int guess = 0;
        int attempts = 0;
        
        // 模拟猜数字过程
        int[] guesses = {10, 30, 40, 42};
        int index = 0;
        
        while (guess != target && index < guesses.length) {
            guess = guesses[index];
            attempts++;
            
            if (guess < target) {
                System.out.println("猜 " + guess + "，太小了");
            } else if (guess > target) {
                System.out.println("猜 " + guess + "，太大了");
            } else {
                System.out.println("猜 " + guess + "，恭喜你猜对了！用了 " + attempts + " 次");
            }
            index++;
        }
        
        // 无限循环（需要 break 退出）
        System.out.println("\n=== 无限循环示例 ===");
        int x = 0;
        while (true) {
            x++;
            if (x > 5) {
                System.out.println("x = " + x + "，退出循环");
                break;
            }
            System.out.println("x = " + x);
        }
    }
}
```

#### do-while 循环

```java
public class DoWhileDemo {
    public static void main(String[] args) {
        // do-while 至少执行一次
        System.out.println("=== do-while 循环 ===");
        int i = 1;
        do {
            System.out.println("i = " + i);
            i++;
        } while (i <= 5);
        
        // 即使条件一开始就不满足，也会执行一次
        System.out.println("\n=== 条件一开始就不满足 ===");
        int j = 10;
        do {
            System.out.println("j = " + j);  // 仍然会执行一次
            j++;
        } while (j < 5);
        
        // 实际应用：菜单系统
        System.out.println("\n=== 模拟菜单系统 ===");
        int choice = 0;
        int[] choices = {1, 2, 3};  // 模拟用户输入
        int idx = 0;
        
        do {
            System.out.println("===== 主菜单 =====");
            System.out.println("1. 查看信息");
            System.out.println("2. 修改设置");
            System.out.println("3. 退出");
            
            if (idx < choices.length) {
                choice = choices[idx++];
                System.out.println("用户选择: " + choice);
            } else {
                break;
            }
            
            switch (choice) {
                case 1:
                    System.out.println("→ 显示用户信息");
                    break;
                case 2:
                    System.out.println("→ 进入设置页面");
                    break;
                case 3:
                    System.out.println("→ 退出系统");
                    break;
                default:
                    System.out.println("→ 无效选择");
            }
            System.out.println();
        } while (choice != 3);
    }
}
```

#### break 和 continue

```java
public class BreakContinueDemo {
    public static void main(String[] args) {
        // break：跳出整个循环
        System.out.println("=== break 示例 ===");
        for (int i = 1; i <= 10; i++) {
            if (i == 5) {
                System.out.println("遇到 5，跳出循环");
                break;
            }
            System.out.println("i = " + i);
        }
        
        // continue：跳过本次循环，继续下一次
        System.out.println("\n=== continue 示例 ===");
        for (int i = 1; i <= 10; i++) {
            if (i % 2 == 0) {
                continue;  // 跳过偶数
            }
            System.out.println("奇数: i = " + i);
        }
        
        // 带标签的 break（跳出多层循环）
        System.out.println("\n=== 带标签的 break ===");
        outer:
        for (int i = 1; i <= 3; i++) {
            for (int j = 1; j <= 3; j++) {
                if (i == 2 && j == 2) {
                    System.out.println("i=" + i + ", j=" + j + "，跳出外层循环");
                    break outer;  // 跳出外层循环
                }
                System.out.println("i=" + i + ", j=" + j);
            }
        }
        
        // 实际应用：查找第一个满足条件的元素
        System.out.println("\n=== 查找示例 ===");
        int[] numbers = {3, 7, 12, 5, 18, 9};
        int firstEven = -1;
        
        for (int num : numbers) {
            if (num % 2 == 0) {
                firstEven = num;
                break;  // 找到第一个偶数就停止
            }
        }
        System.out.println("第一个偶数: " + firstEven);  // 12
        
        // 过滤示例：打印所有奇数
        System.out.println("\n=== 过滤示例 ===");
        for (int num : numbers) {
            if (num % 2 == 0) {
                continue;  // 跳过偶数
            }
            System.out.println("奇数: " + num);
        }
    }
}
```

---

## 六、数组

### 6.1 一维数组

```java
public class ArrayDemo {
    public static void main(String[] args) {
        // ====== 数组声明 ======
        // 方式一：推荐
        int[] numbers;
        
        // 方式二：C 风格（也合法）
        int values[];
        
        // ====== 数组初始化 ======
        // 方式一：静态初始化（声明时直接赋值）
        int[] arr1 = {1, 2, 3, 4, 5};
        
        // 方式二：动态初始化（指定长度，元素为默认值）
        int[] arr2 = new int[5];     // 默认值: 0, 0, 0, 0, 0
        String[] arr3 = new String[3]; // 默认值: null, null, null
        
        // ====== 访问和修改元素 ======
        System.out.println("=== 数组元素访问 ===");
        System.out.println("arr1[0] = " + arr1[0]);  // 第一个元素
        System.out.println("arr1[4] = " + arr1[4]);  // 最后一个元素
        System.out.println("数组长度: " + arr1.length);  // 5
        
        // 修改元素
        arr1[2] = 100;
        System.out.println("修改后 arr1[2] = " + arr1[2]);
        
        // ====== 遍历数组 ======
        System.out.println("\n=== 遍历数组 ===");
        
        // 方式一：普通 for 循环
        System.out.println("普通 for 循环:");
        for (int i = 0; i < arr1.length; i++) {
            System.out.print(arr1[i] + " ");
        }
        System.out.println();
        
        // 方式二：增强 for 循环（for-each）
        System.out.println("增强 for 循环:");
        for (int num : arr1) {
            System.out.print(num + " ");
        }
        System.out.println();
        
        // ====== 数组常用操作 ======
        System.out.println("\n=== 数组常用操作 ===");
        int[] data = {5, 3, 8, 1, 9, 2, 7};
        
        // 求最大值
        int max = data[0];
        for (int i = 1; i < data.length; i++) {
            if (data[i] > max) {
                max = data[i];
            }
        }
        System.out.println("最大值: " + max);
        
        // 求和
        int sum = 0;
        for (int num : data) {
            sum += num;
        }
        System.out.println("总和: " + sum);
        
        // 求平均值
        double avg = (double) sum / data.length;
        System.out.println("平均值: " + avg);
        
        // ====== Arrays 工具类 ======
        System.out.println("\n=== Arrays 工具类 ===");
        int[] sortArr = {5, 3, 8, 1, 9};
        
        // 排序
        java.util.Arrays.sort(sortArr);
        System.out.println("排序后: " + java.util.Arrays.toString(sortArr));
        
        // 二分查找（需要先排序）
        int index = java.util.Arrays.binarySearch(sortArr, 8);
        System.out.println("8 的索引: " + index);
        
        // 填充
        int[] fillArr = new int[5];
        java.util.Arrays.fill(fillArr, 10);
        System.out.println("填充后: " + java.util.Arrays.toString(fillArr));
        
        // 复制
        int[] copyArr = java.util.Arrays.copyOf(sortArr, 3);
        System.out.println("复制前3个: " + java.util.Arrays.toString(copyArr));
    }
}
```

### 6.2 二维数组

```java
public class TwoDimensionalArray {
    public static void main(String[] args) {
        // ====== 二维数组声明和初始化 ======
        // 方式一：静态初始化
        int[][] matrix1 = {
            {1, 2, 3},
            {4, 5, 6},
            {7, 8, 9}
        };
        
        // 方式二：动态初始化
        int[][] matrix2 = new int[3][4];  // 3行4列
        
        // 方式三：不规则数组（每行长度可以不同）
        int[][] irregular = new int[3][];
        irregular[0] = new int[2];  // 第0行2列
        irregular[1] = new int[3];  // 第1行3列
        irregular[2] = new int[4];  // 第2行4列
        
        // ====== 访问元素 ======
        System.out.println("=== 访问二维数组元素 ===");
        System.out.println("matrix1[0][0] = " + matrix1[0][0]);  // 1
        System.out.println("matrix1[1][2] = " + matrix1[1][2]);  // 6
        System.out.println("matrix1[2][1] = " + matrix1[2][1]);  // 8
        
        // ====== 遍历二维数组 ======
        System.out.println("\n=== 遍历二维数组 ===");
        for (int i = 0; i < matrix1.length; i++) {
            for (int j = 0; j < matrix1[i].length; j++) {
                System.out.print(matrix1[i][j] + "\t");
            }
            System.out.println();
        }
        
        // 增强 for 循环遍历
        System.out.println("\n=== 增强 for 循环遍历 ===");
        for (int[] row : matrix1) {
            for (int val : row) {
                System.out.print(val + "\t");
            }
            System.out.println();
        }
        
        // ====== 实际应用：矩阵转置 ======
        System.out.println("\n=== 矩阵转置 ===");
        int[][] original = {
            {1, 2, 3},
            {4, 5, 6}
        };
        
        System.out.println("原矩阵:");
        printMatrix(original);
        
        // 转置：行变列，列变行
        int[][] transposed = new int[original[0].length][original.length];
        for (int i = 0; i < original.length; i++) {
            for (int j = 0; j < original[i].length; j++) {
                transposed[j][i] = original[i][j];
            }
        }
        
        System.out.println("转置后:");
        printMatrix(transposed);
        
        // ====== 实际应用：杨辉三角 ======
        System.out.println("\n=== 杨辉三角 ===");
        int rows = 6;
        int[][] triangle = new int[rows][];
        
        for (int i = 0; i < rows; i++) {
            triangle[i] = new int[i + 1];
            triangle[i][0] = 1;          // 每行第一个为1
            triangle[i][i] = 1;          // 每行最后一个为1
            
            for (int j = 1; j < i; j++) {
                triangle[i][j] = triangle[i-1][j-1] + triangle[i-1][j];
            }
        }
        
        // 打印杨辉三角
        for (int i = 0; i < rows; i++) {
            // 打印前导空格
            for (int k = 0; k < rows - i - 1; k++) {
                System.out.print("  ");
            }
            // 打印数字
            for (int j = 0; j <= i; j++) {
                System.out.printf("%4d", triangle[i][j]);
            }
            System.out.println();
        }
    }
    
    // 辅助方法：打印矩阵
    public static void printMatrix(int[][] matrix) {
        for (int[] row : matrix) {
            for (int val : row) {
                System.out.print(val + "\t");
            }
            System.out.println();
        }
    }
}
```

---

## 七、方法

### 7.1 方法定义与调用

```java
public class MethodDemo {
    
    // ====== 无参数无返回值的方法 ======
    public static void sayHello() {
        System.out.println("Hello, World!");
    }
    
    // ====== 有参数无返回值的方法 ======
    public static void greet(String name) {
        System.out.println("Hello, " + name + "!");
    }
    
    // ====== 有参数有返回值的方法 ======
    public static int add(int a, int b) {
        return a + b;
    }
    
    // ====== 多参数方法 ======
    public static double calculateAverage(double... numbers) {
        // 可变参数（varargs）
        if (numbers.length == 0) {
            return 0;
        }
        double sum = 0;
        for (double num : numbers) {
            sum += num;
        }
        return sum / numbers.length;
    }
    
    public static void main(String[] args) {
        // 调用无参方法
        sayHello();
        
        // 调用有参方法
        greet("张三");
        greet("李四");
        
        // 调用有返回值的方法
        int result = add(10, 20);
        System.out.println("10 + 20 = " + result);
        
        // 调用可变参数方法
        double avg1 = calculateAverage(10, 20, 30);
        double avg2 = calculateAverage(1, 2, 3, 4, 5);
        System.out.println("平均值1: " + avg1);
        System.out.println("平均值2: " + avg2);
    }
}
```

### 7.2 参数传递

```java
public class ParameterPassing {
    
    // 基本类型参数：值传递（传递的是值的副本）
    public static void modifyPrimitive(int x) {
        x = 100;  // 只修改了副本，不影响原始值
        System.out.println("方法内 x = " + x);
    }
    
    // 引用类型参数：传递的是引用的副本（指向同一个对象）
    public static void modifyArray(int[] arr) {
        arr[0] = 100;  // 修改了原始数组的内容
        System.out.println("方法内 arr[0] = " + arr[0]);
    }
    
    // 交换两个数（演示值传递）
    public static void swap(int a, int b) {
        int temp = a;
        a = b;
        b = temp;
        System.out.println("方法内: a = " + a + ", b = " + b);
    }
    
    public static void main(String[] args) {
        // 基本类型参数
        System.out.println("=== 基本类型参数（值传递）===");
        int num = 10;
        System.out.println("调用前 num = " + num);
        modifyPrimitive(num);
        System.out.println("调用后 num = " + num);  // 仍然是 10
        
        // 引用类型参数
        System.out.println("\n=== 引用类型参数（引用传递）===");
        int[] array = {1, 2, 3};
        System.out.println("调用前 array[0] = " + array[0]);
        modifyArray(array);
        System.out.println("调用后 array[0] = " + array[0]);  // 变成 100
        
        // 交换示例
        System.out.println("\n=== 交换示例 ===");
        int a = 10, b = 20;
        System.out.println("交换前: a = " + a + ", b = " + b);
        swap(a, b);
        System.out.println("交换后: a = " + a + ", b = " + b);  // 没有交换
    }
}
```

### 7.3 方法重载

```java
public class MethodOverloading {
    
    // 重载：方法名相同，参数列表不同（参数类型、个数或顺序不同）
    
    // 版本1：两个 int 参数
    public static int add(int a, int b) {
        System.out.println("调用 add(int, int)");
        return a + b;
    }
    
    // 版本2：三个 int 参数
    public static int add(int a, int b, int c) {
        System.out.println("调用 add(int, int, int)");
        return a + b + c;
    }
    
    // 版本3：两个 double 参数
    public static double add(double a, double b) {
        System.out.println("调用 add(double, double)");
        return a + b;
    }
    
    // 版本4：不同类型参数
    public static String add(String a, String b) {
        System.out.println("调用 add(String, String)");
        return a + b;
    }
    
    // 注意：仅返回值类型不同不算重载（会编译错误）
    // public static double add(int a, int b) { return a + b; }  // 错误！
    
    // 实际应用：打印方法重载
    public static void print(int value) {
        System.out.println("整数: " + value);
    }
    
    public static void print(double value) {
        System.out.println("浮点数: " + value);
    }
    
    public static void print(String value) {
        System.out.println("字符串: " + value);
    }
    
    public static void print(int[] values) {
        System.out.print("数组: [");
        for (int i = 0; i < values.length; i++) {
            System.out.print(values[i]);
            if (i < values.length - 1) System.out.print(", ");
        }
        System.out.println("]");
    }
    
    public static void main(String[] args) {
        // 调用不同的重载方法
        System.out.println("=== 方法重载示例 ===");
        System.out.println("add(1, 2) = " + add(1, 2));
        System.out.println("add(1, 2, 3) = " + add(1, 2, 3));
        System.out.println("add(1.5, 2.5) = " + add(1.5, 2.5));
        System.out.println("add(\"Hello\", \" World\") = " + add("Hello", " World"));
        
        // 打印方法重载
        System.out.println("\n=== 打印方法重载 ===");
        print(100);
        print(3.14);
        print("Hello");
        print(new int[]{1, 2, 3, 4, 5});
    }
}
```

### 7.4 递归方法

```java
public class RecursionDemo {
    
    // 阶乘：n! = n × (n-1) × ... × 1
    public static long factorial(int n) {
        if (n <= 1) {
            return 1;  // 基线条件（递归出口）
        }
        return n * factorial(n - 1);  // 递归调用
    }
    
    // 斐波那契数列：F(n) = F(n-1) + F(n-2)
    public static long fibonacci(int n) {
        if (n <= 1) {
            return n;  // F(0)=0, F(1)=1
        }
        return fibonacci(n - 1) + fibonacci(n - 2);
    }
    
    // 二分查找（递归版本）
    public static int binarySearch(int[] arr, int target, int left, int right) {
        if (left > right) {
            return -1;  // 未找到
        }
        
        int mid = left + (right - left) / 2;
        
        if (arr[mid] == target) {
            return mid;
        } else if (arr[mid] > target) {
            return binarySearch(arr, target, left, mid - 1);
        } else {
            return binarySearch(arr, target, mid + 1, right);
        }
    }
    
    // 汉诺塔
    public static void hanoi(int n, char from, char to, char helper) {
        if (n == 1) {
            System.out.println("移动盘子 1 从 " + from + " 到 " + to);
            return;
        }
        hanoi(n - 1, from, helper, to);
        System.out.println("移动盘子 " + n + " 从 " + from + " 到 " + to);
        hanoi(n - 1, helper, to, from);
    }
    
    public static void main(String[] args) {
        // 阶乘
        System.out.println("=== 阶乘 ===");
        for (int i = 1; i <= 10; i++) {
            System.out.println(i + "! = " + factorial(i));
        }
        
        // 斐波那契数列
        System.out.println("\n=== 斐波那契数列 ===");
        System.out.print("前 10 项: ");
        for (int i = 0; i < 10; i++) {
            System.out.print(fibonacci(i) + " ");
        }
        System.out.println();
        
        // 二分查找
        System.out.println("\n=== 二分查找 ===");
        int[] sorted = {1, 3, 5, 7, 9, 11, 13, 15, 17, 19};
        int target = 11;
        int index = binarySearch(sorted, target, 0, sorted.length - 1);
        System.out.println("数组: " + java.util.Arrays.toString(sorted));
        System.out.println("查找 " + target + "，索引: " + index);
        
        // 汉诺塔
        System.out.println("\n=== 汉诺塔（3个盘子）===");
        hanoi(3, 'A', 'C', 'B');
    }
}
```

---

## 八、面向对象基础

### 8.1 类与对象

```java
// 定义一个 Student 类
class Student {
    // 属性（成员变量）
    private String name;       // 姓名
    private int age;           // 年龄
    private String studentId;  // 学号
    private double[] scores;   // 成绩数组
    
    // 构造方法（与类名同名，无返回值类型）
    public Student() {
        // 无参构造方法
        this.name = "未知";
        this.age = 0;
        this.studentId = "000000";
        this.scores = new double[0];
    }
    
    public Student(String name, int age, String studentId) {
        // 有参构造方法
        this.name = name;
        this.age = age;
        this.studentId = studentId;
        this.scores = new double[0];
    }
    
    // 方法（行为）
    public void introduce() {
        System.out.println("大家好，我是 " + name + "，今年 " + age + " 岁，学号 " + studentId);
    }
    
    public void setScores(double... scores) {
        this.scores = scores;
    }
    
    public double getAverage() {
        if (scores.length == 0) return 0;
        double sum = 0;
        for (double score : scores) {
            sum += score;
        }
        return sum / scores.length;
    }
    
    // Getter 和 Setter 方法
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public int getAge() { return age; }
    public void setAge(int age) {
        if (age > 0 && age < 150) {
            this.age = age;
        }
    }
    
    // toString 方法（对象的字符串表示）
    @Override
    public String toString() {
        return "Student{name='" + name + "', age=" + age + ", studentId='" + studentId + "'}";
    }
}

public class ClassAndObject {
    public static void main(String[] args) {
        // 创建对象
        Student student1 = new Student();  // 使用无参构造方法
        student1.setName("张三");
        student1.setAge(20);
        
        Student student2 = new Student("李四", 21, "2024002");  // 使用有参构造方法
        student2.setScores(85, 90, 92, 78);
        
        // 使用对象
        student1.introduce();
        student2.introduce();
        
        System.out.println(student2.getName() + " 的平均分: " + student2.getAverage());
        System.out.println("student2 对象: " + student2.toString());
    }
}
```

### 8.2 封装

```java
// 封装：将数据（属性）和操作数据的方法绑定在一起，隐藏内部实现细节
class BankAccount {
    // 私有属性：外部无法直接访问
    private String accountNo;
    private String owner;
    private double balance;
    private static double interestRate = 0.03;  // 静态属性：所有对象共享
    
    // 构造方法
    public BankAccount(String accountNo, String owner, double initialBalance) {
        this.accountNo = accountNo;
        this.owner = owner;
        if (initialBalance >= 0) {
            this.balance = initialBalance;
        } else {
            this.balance = 0;
            System.out.println("初始余额不能为负数，已设为 0");
        }
    }
    
    // 存款方法
    public void deposit(double amount) {
        if (amount > 0) {
            balance += amount;
            System.out.println("存款成功: " + amount + "，当前余额: " + balance);
        } else {
            System.out.println("存款金额必须大于 0");
        }
    }
    
    // 取款方法（包含业务逻辑验证）
    public boolean withdraw(double amount) {
        if (amount <= 0) {
            System.out.println("取款金额必须大于 0");
            return false;
        }
        if (amount > balance) {
            System.out.println("余额不足，当前余额: " + balance);
            return false;
        }
        balance -= amount;
        System.out.println("取款成功: " + amount + "，当前余额: " + balance);
        return true;
    }
    
    // 查询余额（只读方法）
    public double getBalance() {
        return balance;
    }
    
    // 转账方法
    public boolean transfer(BankAccount target, double amount) {
        if (this.withdraw(amount)) {
            target.deposit(amount);
            return true;
        }
        return false;
    }
    
    // Getter（只读属性）
    public String getAccountNo() { return accountNo; }
    public String getOwner() { return owner; }
    
    // 静态方法
    public static void setInterestRate(double rate) {
        if (rate >= 0 && rate <= 1) {
            interestRate = rate;
        }
    }
    
    public static double getInterestRate() {
        return interestRate;
    }
    
    // 显示账户信息
    @Override
    public String toString() {
        return "BankAccount{账号='" + accountNo + "', 户主='" + owner + "', 余额=" + balance + "}";
    }
}

public class EncapsulationDemo {
    public static void main(String[] args) {
        // 创建账户
        BankAccount account1 = new BankAccount("622200001", "张三", 10000);
        BankAccount account2 = new BankAccount("622200002", "李四", 5000);
        
        // 存款取款
        account1.deposit(5000);
        account1.withdraw(3000);
        
        // 转账
        System.out.println("\n--- 转账操作 ---");
        account1.transfer(account2, 2000);
        
        // 查看余额
        System.out.println("\n--- 账户信息 ---");
        System.out.println(account1);
        System.out.println(account2);
        
        // 静态属性
        System.out.println("\n当前利率: " + BankAccount.getInterestRate());
        BankAccount.setInterestRate(0.035);
        System.out.println("调整后利率: " + BankAccount.getInterestRate());
    }
}
```

### 8.3 继承

```java
// 父类（基类）
class Animal {
    protected String name;
    protected int age;
    
    public Animal(String name, int age) {
        this.name = name;
        this.age = age;
        System.out.println("Animal 构造方法被调用");
    }
    
    public void eat() {
        System.out.println(name + " 在吃东西");
    }
    
    public void sleep() {
        System.out.println(name + " 在睡觉");
    }
    
    public void introduce() {
        System.out.println("我是 " + name + "，今年 " + age + " 岁");
    }
    
    @Override
    public String toString() {
        return "Animal{name='" + name + "', age=" + age + "}";
    }
}

// 子类（派生类）：继承 Animal
class Dog extends Animal {
    private String breed;  // 品种
    
    public Dog(String name, int age, String breed) {
        super(name, age);  // 调用父类构造方法（必须是第一行）
        this.breed = breed;
        System.out.println("Dog 构造方法被调用");
    }
    
    // 子类特有方法
    public void bark() {
        System.out.println(name + " 在汪汪叫");
    }
    
    public void fetch() {
        System.out.println(name + " 在捡球");
    }
    
    // 方法重写（Override）
    @Override
    public void introduce() {
        super.introduce();  // 调用父类方法
        System.out.println("我是一只 " + breed + " 狗");
    }
    
    @Override
    public String toString() {
        return "Dog{name='" + name + "', age=" + age + ", breed='" + breed + "'}";
    }
}

// 另一个子类
class Cat extends Animal {
    private boolean isIndoor;
    
    public Cat(String name, int age, boolean isIndoor) {
        super(name, age);
        this.isIndoor = isIndoor;
    }
    
    public void meow() {
        System.out.println(name + " 在喵喵叫");
    }
    
    @Override
    public void introduce() {
        super.introduce();
        System.out.println("我是一只" + (isIndoor ? "家" : "野") + "猫");
    }
}

public class InheritanceDemo {
    public static void main(String[] args) {
        // 创建子类对象
        System.out.println("=== 创建 Dog 对象 ===");
        Dog dog = new Dog("旺财", 3, "金毛");
        
        System.out.println("\n=== 创建 Cat 对象 ===");
        Cat cat = new Cat("咪咪", 2, true);
        
        // 调用继承的方法
        System.out.println("\n=== 调用继承的方法 ===");
        dog.eat();     // 继承自 Animal
        dog.sleep();   // 继承自 Animal
        cat.eat();
        cat.sleep();
        
        // 调用子类特有方法
        System.out.println("\n=== 调用子类特有方法 ===");
        dog.bark();    // Dog 特有
        dog.fetch();   // Dog 特有
        cat.meow();    // Cat 特有
        
        // 调用重写的方法
        System.out.println("\n=== 调用重写的方法 ===");
        dog.introduce();  // 调用 Dog 的 introduce
        cat.introduce();  // 调用 Cat 的 introduce
        
        // 向上转型（子类 → 父类）
        System.out.println("\n=== 向上转型 ===");
        Animal animal1 = new Dog("小黑", 5, "哈士奇");
        Animal animal2 = new Cat("花花", 1, false);
        
        animal1.introduce();  // 实际调用 Dog 的 introduce（动态绑定）
        animal2.introduce();  // 实际调用 Cat 的 introduce
        // animal1.bark();    // 编译错误：Animal 类型没有 bark 方法
    }
}
```

### 8.4 多态

```java
// 多态：同一操作作用于不同对象，产生不同的行为

// 抽象类
abstract class Shape {
    protected String color;
    
    public Shape(String color) {
        this.color = color;
    }
    
    // 抽象方法：子类必须实现
    public abstract double getArea();
    public abstract double getPerimeter();
    
    // 普通方法
    public void display() {
        System.out.println("颜色: " + color + ", 面积: " + String.format("%.2f", getArea()) 
            + ", 周长: " + String.format("%.2f", getPerimeter()));
    }
}

// 圆形
class Circle extends Shape {
    private double radius;
    
    public Circle(String color, double radius) {
        super(color);
        this.radius = radius;
    }
    
    @Override
    public double getArea() {
        return Math.PI * radius * radius;
    }
    
    @Override
    public double getPerimeter() {
        return 2 * Math.PI * radius;
    }
}

// 矩形
class Rectangle extends Shape {
    private double width;
    private double height;
    
    public Rectangle(String color, double width, double height) {
        super(color);
        this.width = width;
        this.height = height;
    }
    
    @Override
    public double getArea() {
        return width * height;
    }
    
    @Override
    public double getPerimeter() {
        return 2 * (width + height);
    }
}

// 三角形
class Triangle extends Shape {
    private double a, b, c;  // 三边
    
    public Triangle(String color, double a, double b, double c) {
        super(color);
        this.a = a;
        this.b = b;
        this.c = c;
    }
    
    @Override
    public double getArea() {
        // 海伦公式
        double s = (a + b + c) / 2;
        return Math.sqrt(s * (s - a) * (s - b) * (s - c));
    }
    
    @Override
    public double getPerimeter() {
        return a + b + c;
    }
}

public class PolymorphismDemo {
    
    // 方法参数使用父类类型（多态的体现）
    public static void printShapeInfo(Shape shape) {
        System.out.print("这是一个图形 → ");
        shape.display();  // 运行时根据实际类型调用对应的方法
    }
    
    public static void main(String[] args) {
        // 创建不同形状
        Shape circle = new Circle("红色", 5);
        Shape rectangle = new Rectangle("蓝色", 4, 6);
        Shape triangle = new Triangle("绿色", 3, 4, 5);
        
        // 多态：父类引用指向子类对象
        System.out.println("=== 多态示例 ===");
        circle.display();
        rectangle.display();
        triangle.display();
        
        // 使用数组存储不同类型的对象
        System.out.println("\n=== 对象数组 ===");
        Shape[] shapes = {
            new Circle("黄色", 3),
            new Rectangle("紫色", 5, 8),
            new Triangle("橙色", 6, 8, 10),
            new Circle("白色", 10)
        };
        
        // 遍历并调用方法（多态）
        for (Shape shape : shapes) {
            printShapeInfo(shape);
        }
        
        // 计算所有图形的总面积
        System.out.println("\n=== 计算总面积 ===");
        double totalArea = 0;
        for (Shape shape : shapes) {
            totalArea += shape.getArea();
        }
        System.out.println("所有图形的总面积: " + String.format("%.2f", totalArea));
        
        // instanceof 判断和向下转型
        System.out.println("\n=== instanceof 判断 ===");
        for (Shape shape : shapes) {
            if (shape instanceof Circle) {
                Circle c = (Circle) shape;  // 向下转型
                System.out.println("圆形，半径: " + c.getArea() / Math.PI);
            } else if (shape instanceof Rectangle) {
                System.out.println("矩形");
            } else if (shape instanceof Triangle) {
                System.out.println("三角形");
            }
        }
    }
}
```

### 8.5 接口

```java
// 接口：定义行为规范（Java 8+ 可以有默认方法和静态方法）

// 定义接口
interface Flyable {
    // 抽象方法（默认 public abstract）
    void fly();
    
    // 默认方法（Java 8+）
    default void land() {
        System.out.println("正在降落...");
    }
    
    // 静态方法（Java 8+）
    static void checkWeather() {
        System.out.println("检查天气状况...");
    }
}

interface Swimmable {
    void swim();
}

interface Runnable {
    void run();
}

// 类可以实现多个接口
class Duck implements Flyable, Swimmable, Runnable {
    private String name;
    
    public Duck(String name) {
        this.name = name;
    }
    
    @Override
    public void fly() {
        System.out.println(name + " 在飞");
    }
    
    @Override
    public void swim() {
        System.out.println(name + " 在游泳");
    }
    
    @Override
    public void run() {
        System.out.println(name + " 在跑");
    }
    
    // 可以重写接口的默认方法
    @Override
    public void land() {
        System.out.println(name + " 降落在湖面上");
    }
}

// 接口继承
interface Vehicle {
    void start();
    void stop();
}

interface ElectricVehicle extends Vehicle {
    void charge();
}

class ElectricCar implements ElectricVehicle {
    private String model;
    
    public ElectricCar(String model) {
        this.model = model;
    }
    
    @Override
    public void start() {
        System.out.println(model + " 启动");
    }
    
    @Override
    public void stop() {
        System.out.println(model + " 停止");
    }
    
    @Override
    public void charge() {
        System.out.println(model + " 充电中...");
    }
}

public class InterfaceDemo {
    public static void main(String[] args) {
        // 使用接口
        Duck duck = new Duck("唐老鸭");
        duck.fly();
        duck.swim();
        duck.run();
        duck.land();
        
        // 接口静态方法
        Flyable.checkWeather();
        
        // 多态：接口引用指向实现类
        System.out.println("\n=== 接口多态 ===");
        Flyable flyable = new Duck("达菲鸭");
        flyable.fly();
        // flyable.swim();  // 编译错误：Flyable 接口没有 swim 方法
        
        // 电动车
        System.out.println("\n=== 接口继承 ===");
        ElectricCar car = new ElectricCar("Tesla Model 3");
        car.start();
        car.charge();
        car.stop();
        
        // 接口作为方法参数
        System.out.println("\n=== 接口作为参数 ===");
        performAction(duck);
    }
    
    // 接口作为方法参数
    public static void performAction(Flyable flyable) {
        System.out.println("执行飞行操作:");
        flyable.fly();
    }
}
```

---

## 九、字符串处理

### 9.1 String 类

```java
public class StringDemo {
    public static void main(String[] args) {
        // ====== 字符串创建 ======
        String s1 = "Hello";           // 字符串常量池
        String s2 = new String("Hello"); // 堆中创建新对象
        String s3 = "Hello";
        
        // == 比较引用，equals 比较内容
        System.out.println("s1 == s2: " + (s1 == s2));       // false（不同对象）
        System.out.println("s1 == s3: " + (s1 == s3));       // true（同一常量池对象）
        System.out.println("s1.equals(s2): " + s1.equals(s2)); // true（内容相同）
        
        // ====== 常用方法 ======
        String str = "Hello, World!";
        
        // 长度
        System.out.println("\n长度: " + str.length());  // 13
        
        // 字符访问
        System.out.println("第0个字符: " + str.charAt(0));  // H
        System.out.println("最后一个字符: " + str.charAt(str.length() - 1));  // !
        
        // 截取
        System.out.println("截取(0,5): " + str.substring(0, 5));  // Hello
        System.out.println("截取(7): " + str.substring(7));       // World!
        
        // 查找
        System.out.println("indexOf('World'): " + str.indexOf("World"));  // 7
        System.out.println("contains('Hello'): " + str.contains("Hello")); // true
        System.out.println("startsWith('Hello'): " + str.startsWith("Hello")); // true
        System.out.println("endsWith('!'): " + str.endsWith("!"));  // true
        
        // 大小写转换
        System.out.println("toUpperCase: " + str.toUpperCase());
        System.out.println("toLowerCase: " + str.toLowerCase());
        
        // 去除空白
        String padded = "  Hello  ";
        System.out.println("trim: '" + padded.trim() + "'");
        
        // 替换
        System.out.println("replace: " + str.replace("World", "Java"));
        
        // 分割
        String csv = "apple,banana,orange";
        String[] fruits = csv.split(",");
        System.out.println("分割结果:");
        for (String fruit : fruits) {
            System.out.println("  - " + fruit);
        }
        
        // 连接
        String joined = String.join(" | ", fruits);
        System.out.println("连接: " + joined);
        
        // 格式化
        String formatted = String.format("姓名: %s, 年龄: %d, 成绩: %.2f", "张三", 20, 95.5);
        System.out.println("格式化: " + formatted);
    }
}
```

### 9.2 StringBuilder 和 StringBuffer

```java
public class StringBuilderDemo {
    public static void main(String[] args) {
        // ====== String 拼接性能问题 ======
        // String 是不可变的，每次拼接都创建新对象
        long start = System.currentTimeMillis();
        String result = "";
        for (int i = 0; i < 10000; i++) {
            result += i;  // 性能差！
        }
        long end = System.currentTimeMillis();
        System.out.println("String 拼接耗时: " + (end - start) + "ms");
        
        // ====== StringBuilder（推荐，非线程安全，性能高）======
        start = System.currentTimeMillis();
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 10000; i++) {
            sb.append(i);
        }
        end = System.currentTimeMillis();
        System.out.println("StringBuilder 拼接耗时: " + (end - start) + "ms");
        
        // ====== 常用方法 ======
        StringBuilder builder = new StringBuilder("Hello");
        
        // 追加
        builder.append(" World");
        builder.append(123);
        builder.append(true);
        System.out.println("append: " + builder);
        
        // 插入
        builder.insert(5, ",");
        System.out.println("insert: " + builder);
        
        // 删除
        builder.delete(5, 6);
        System.out.println("delete: " + builder);
        
        // 替换
        builder.replace(0, 5, "Hi");
        System.out.println("replace: " + builder);
        
        // 反转
        builder.reverse();
        System.out.println("reverse: " + builder);
        
        // ====== 实际应用：拼接 SQL ======
        System.out.println("\n=== 拼接 SQL ===");
        String[] columns = {"id", "name", "age", "email"};
        StringBuilder sql = new StringBuilder("SELECT ");
        sql.append(String.join(", ", columns));
        sql.append(" FROM users WHERE age > 18 ORDER BY name");
        System.out.println(sql);
    }
}
```

---

## 十、异常处理

### 10.1 异常类型

```java
public class ExceptionDemo {
    public static void main(String[] args) {
        // ====== 常见异常类型 ======
        
        // 1. ArithmeticException：算术异常
        try {
            int result = 10 / 0;
        } catch (ArithmeticException e) {
            System.out.println("算术异常: " + e.getMessage());
        }
        
        // 2. ArrayIndexOutOfBoundsException：数组越界
        try {
            int[] arr = {1, 2, 3};
            int val = arr[5];
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("数组越界: " + e.getMessage());
        }
        
        // 3. NullPointerException：空指针
        try {
            String str = null;
            int len = str.length();
        } catch (NullPointerException e) {
            System.out.println("空指针异常: " + e.getMessage());
        }
        
        // 4. NumberFormatException：数字格式
        try {
            int num = Integer.parseInt("abc");
        } catch (NumberFormatException e) {
            System.out.println("数字格式异常: " + e.getMessage());
        }
        
        // 5. ClassCastException：类型转换
        try {
            Object obj = "Hello";
            Integer num = (Integer) obj;
        } catch (ClassCastException e) {
            System.out.println("类型转换异常: " + e.getMessage());
        }
    }
}
```

### 10.2 try-catch-finally

```java
public class TryCatchFinally {
    
    public static void divide(int a, int b) {
        try {
            System.out.println("尝试计算 " + a + " / " + b);
            int result = a / b;
            System.out.println("结果: " + result);
        } catch (ArithmeticException e) {
            System.out.println("捕获异常: 除数不能为 0");
        } finally {
            // finally 块总是执行（用于释放资源）
            System.out.println("finally 块执行（清理资源）");
        }
        System.out.println("方法继续执行...\n");
    }
    
    public static void multiCatch() {
        try {
            int[] arr = {1, 2, 3};
            int result = arr[Integer.parseInt("abc")];
        } catch (NumberFormatException e) {
            System.out.println("数字格式错误: " + e.getMessage());
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("数组越界: " + e.getMessage());
        } catch (Exception e) {
            // 捕获所有异常（放在最后）
            System.out.println("其他异常: " + e.getMessage());
        } finally {
            System.out.println("finally 块执行");
        }
    }
    
    // try-with-resources（Java 7+，自动关闭资源）
    public static void tryWithResources() {
        // 自动关闭实现了 AutoCloseable 接口的资源
        try (java.io.FileReader reader = new java.io.FileReader("test.txt")) {
            int content = reader.read();
            System.out.println("读取内容: " + (char) content);
        } catch (java.io.FileNotFoundException e) {
            System.out.println("文件不存在");
        } catch (java.io.IOException e) {
            System.out.println("IO 异常: " + e.getMessage());
        }
        // reader 在这里自动关闭，无需 finally
    }
    
    public static void main(String[] args) {
        System.out.println("=== 基本 try-catch-finally ===");
        divide(10, 2);
        divide(10, 0);
        
        System.out.println("=== 多重 catch ===");
        multiCatch();
        
        System.out.println("\n=== try-with-resources ===");
        tryWithResources();
    }
}
```

### 10.3 自定义异常

```java
// 自定义异常类
class InsufficientFundsException extends Exception {
    private double amount;
    
    public InsufficientFundsException(double amount) {
        super("余额不足，差额: " + amount);
        this.amount = amount;
    }
    
    public double getAmount() {
        return amount;
    }
}

class InvalidAgeException extends RuntimeException {
    public InvalidAgeException(String message) {
        super(message);
    }
}

class Account {
    private double balance;
    
    public Account(double initialBalance) {
        if (initialBalance < 0) {
            throw new InvalidAgeException("初始余额不能为负数");
        }
        this.balance = initialBalance;
    }
    
    // 声明抛出受检异常
    public void withdraw(double amount) throws InsufficientFundsException {
        if (amount > balance) {
            throw new InsufficientFundsException(amount - balance);
        }
        balance -= amount;
        System.out.println("取款成功: " + amount + "，余额: " + balance);
    }
    
    public double getBalance() {
        return balance;
    }
}

public class CustomExceptionDemo {
    public static void main(String[] args) {
        Account account = new Account(1000);
        
        try {
            account.withdraw(500);
            account.withdraw(800);  // 会抛出异常
        } catch (InsufficientFundsException e) {
            System.out.println("取款失败: " + e.getMessage());
            System.out.println("还差: " + e.getAmount());
        }
        
        // RuntimeException 不需要显式捕获
        try {
            Account invalidAccount = new Account(-100);
        } catch (InvalidAgeException e) {
            System.out.println("创建账户失败: " + e.getMessage());
        }
    }
}
```

---

## 十一、线程处理

### 11.1 线程基本概念

**进程与线程的区别：**

| 概念 | 说明 | 特点 |
|-----|------|------|
| **进程** | 操作系统分配资源的基本单位 | 独立内存空间，进程间通信开销大 |
| **线程** | CPU 调度的基本单位 | 共享进程内存，线程间通信高效 |

**多线程的优势：**
- 提高 CPU 利用率
- 提升程序响应速度
- 简化复杂任务的处理

**多线程的风险：**
- 线程安全问题（数据竞争）
- 死锁问题
- 上下文切换开销

### 11.2 线程创建方式

#### 方式一：继承 Thread 类

```java
// 定义线程类
class MyThread extends Thread {
    private String name;
    
    public MyThread(String name) {
        this.name = name;
    }
    
    @Override
    public void run() {
        // 线程执行的任务
        for (int i = 1; i <= 5; i++) {
            System.out.println(name + " 运行: " + i);
            try {
                Thread.sleep(100);  // 休眠 100 毫秒
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}

public class ThreadDemo1 {
    public static void main(String[] args) {
        // 创建线程对象
        MyThread thread1 = new MyThread("线程A");
        MyThread thread2 = new MyThread("线程B");
        
        // 启动线程（不要直接调用 run()）
        thread1.start();
        thread2.start();
        
        // 主线程也在运行
        for (int i = 1; i <= 3; i++) {
            System.out.println("主线程运行: " + i);
        }
    }
}
```

**注意：** Java 不支持多继承，继承 Thread 类后无法继承其他类。

#### 方式二：实现 Runnable 接口（推荐）

```java
// 实现 Runnable 接口
class MyRunnable implements Runnable {
    private String name;
    
    public MyRunnable(String name) {
        this.name = name;
    }
    
    @Override
    public void run() {
        for (int i = 1; i <= 5; i++) {
            System.out.println(name + " 运行: " + i);
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}

public class ThreadDemo2 {
    public static void main(String[] args) {
        // 创建 Runnable 实例
        MyRunnable runnable1 = new MyRunnable("线程A");
        MyRunnable runnable2 = new MyRunnable("线程B");
        
        // 通过 Runnable 创建 Thread 对象
        Thread thread1 = new Thread(runnable1);
        Thread thread2 = new Thread(runnable2);
        
        // 启动线程
        thread1.start();
        thread2.start();
        
        // 也可以使用 Lambda 表达式（Java 8+）
        Thread thread3 = new Thread(() -> {
            System.out.println("Lambda 线程运行");
        });
        thread3.start();
    }
}
```

**优势：**
- 避免单继承限制
- 线程与任务解耦
- 更适合线程池使用

#### 方式三：实现 Callable 接口（有返回值）

```java
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.FutureTask;

// 实现 Callable 接口（可以有返回值和抛出异常）
class MyCallable implements Callable<Integer> {
    private int n;
    
    public MyCallable(int n) {
        this.n = n;
    }
    
    @Override
    public Integer call() throws Exception {
        int sum = 0;
        for (int i = 1; i <= n; i++) {
            sum += i;
            Thread.sleep(10);  // 模拟耗时操作
        }
        return sum;
    }
}

public class CallableDemo {
    public static void main(String[] args) {
        // 创建 Callable 实例
        MyCallable callable = new MyCallable(100);
        
        // 使用 FutureTask 包装 Callable
        FutureTask<Integer> futureTask = new FutureTask<>(callable);
        
        // 创建线程
        Thread thread = new Thread(futureTask);
        thread.start();
        
        try {
            // 获取返回值（会阻塞直到计算完成）
            Integer result = futureTask.get();
            System.out.println("计算结果: " + result);  // 5050
        } catch (InterruptedException | ExecutionException e) {
            e.printStackTrace();
        }
    }
}
```

### 11.3 线程生命周期

线程从创建到销毁经历以下状态：

```
    创建
      ↓
  [新建] ──start()──→ [就绪] ←──yield()──
      ↑                  ↓
      │            获取CPU时间片
      │                  ↓
  sleep()/         [运行中] ──完成──→ [终止]
  wait()/              ↓
  阻塞I/O         [阻塞]
      ↑                ↓
      └────条件满足─────┘
```

| 状态 | 说明 |
|-----|------|
| **新建（New）** | 创建 Thread 对象后，尚未调用 start() |
| **就绪（Runnable）** | 调用 start() 后，等待 CPU 调度 |
| **运行（Running）** | 获得 CPU 时间片，执行 run() 方法 |
| **阻塞（Blocked）** | 等待锁或 I/O，暂时停止执行 |
| **终止（Terminated）** | run() 方法执行完毕或异常退出 |

### 11.4 线程常用方法

```java
public class ThreadMethods {
    public static void main(String[] args) {
        // ====== sleep()：线程休眠 ======
        System.out.println("=== sleep() 示例 ===");
        try {
            System.out.println("开始时间: " + System.currentTimeMillis());
            Thread.sleep(1000);  // 休眠 1 秒
            System.out.println("结束时间: " + System.currentTimeMillis());
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        
        // ====== join()：等待线程结束 ======
        System.out.println("\n=== join() 示例 ===");
        Thread joinThread = new Thread(() -> {
            try {
                for (int i = 1; i <= 3; i++) {
                    System.out.println("子线程: " + i);
                    Thread.sleep(200);
                }
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        });
        
        joinThread.start();
        try {
            joinThread.join();  // 主线程等待子线程结束
            System.out.println("子线程已结束，主线程继续执行");
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        
        // ====== yield()：让出 CPU 时间片 ======
        System.out.println("\n=== yield() 示例 ===");
        Thread yieldThread = new Thread(() -> {
            for (int i = 1; i <= 5; i++) {
                System.out.println("线程运行: " + i);
                if (i == 3) {
                    Thread.yield();  // 让出 CPU，但不释放锁
                    System.out.println("yield() 后继续执行");
                }
            }
        });
        yieldThread.start();
        
        // ====== 线程优先级 ======
        System.out.println("\n=== 线程优先级 ===");
        Thread highPriority = new Thread(() -> {
            System.out.println("高优先级线程");
        });
        highPriority.setPriority(Thread.MAX_PRIORITY);  // 10
        
        Thread lowPriority = new Thread(() -> {
            System.out.println("低优先级线程");
        });
        lowPriority.setPriority(Thread.MIN_PRIORITY);  // 1
        
        highPriority.start();
        lowPriority.start();
        
        // ====== 守护线程 ======
        System.out.println("\n=== 守护线程 ===");
        Thread daemonThread = new Thread(() -> {
            while (true) {
                System.out.println("守护线程运行中...");
                try {
                    Thread.sleep(500);
                } catch (InterruptedException e) {
                    break;
                }
            }
        });
        daemonThread.setDaemon(true);  // 设置为守护线程
        daemonThread.start();
        
        // 主线程结束后，守护线程自动终止
        try {
            Thread.sleep(2000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println("主线程结束");
    }
}
```

### 11.5 线程安全问题

**问题示例：卖票系统**

```java
// 线程不安全的示例
class TicketSeller implements Runnable {
    private int tickets = 100;
    
    @Override
    public void run() {
        while (tickets > 0) {
            System.out.println(Thread.currentThread().getName() + " 卖出第 " + tickets + " 张票");
            tickets--;
            
            // 模拟售票耗时
            try {
                Thread.sleep(10);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}

public class UnsafeThreadDemo {
    public static void main(String[] args) {
        TicketSeller seller = new TicketSeller();
        
        // 创建 3 个窗口
        Thread window1 = new Thread(seller, "窗口1");
        Thread window2 = new Thread(seller, "窗口2");
        Thread window3 = new Thread(seller, "窗口3");
        
        window1.start();
        window2.start();
        window3.start();
        
        // 问题：可能出现重复售票或超卖
        // 原因：多个线程同时访问共享资源，没有同步机制
    }
}
```

**问题分析：**
- 多个线程同时读取 `tickets` 变量
- 一个线程判断 `tickets > 0` 后，另一个线程可能已经修改了 `tickets`
- 导致数据不一致

### 11.6 线程同步机制

#### synchronized 关键字

```java
// 方式一：同步方法
class SafeTicketSeller1 implements Runnable {
    private int tickets = 100;
    
    @Override
    public synchronized void run() {  // 同步整个方法
        while (tickets > 0) {
            System.out.println(Thread.currentThread().getName() + " 卖出第 " + tickets + " 张票");
            tickets--;
            
            try {
                Thread.sleep(10);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}

// 方式二：同步代码块（推荐，更灵活）
class SafeTicketSeller2 implements Runnable {
    private int tickets = 100;
    private final Object lock = new Object();  // 锁对象
    
    @Override
    public void run() {
        while (true) {
            synchronized (lock) {  // 同步代码块
                if (tickets <= 0) break;
                
                System.out.println(Thread.currentThread().getName() + " 卖出第 " + tickets + " 张票");
                tickets--;
            }
            
            try {
                Thread.sleep(10);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}

// 方式三：使用 this 作为锁
class SafeTicketSeller3 implements Runnable {
    private int tickets = 100;
    
    @Override
    public void run() {
        while (true) {
            synchronized (this) {  // 使用当前对象作为锁
                if (tickets <= 0) break;
                
                System.out.println(Thread.currentThread().getName() + " 卖出第 " + tickets + " 张票");
                tickets--;
            }
            
            try {
                Thread.sleep(10);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}

public class SynchronizedDemo {
    public static void main(String[] args) {
        SafeTicketSeller2 seller = new SafeTicketSeller2();
        
        Thread window1 = new Thread(seller, "窗口1");
        Thread window2 = new Thread(seller, "窗口2");
        Thread window3 = new Thread(seller, "窗口3");
        
        window1.start();
        window2.start();
        window3.start();
        
        // 现在不会出现重复售票问题
    }
}
```

**synchronized 原理：**
- 每个对象都有一个内置锁（Monitor）
- 线程进入 synchronized 块时自动获取锁
- 线程退出 synchronized 块时自动释放锁
- 同一时刻只有一个线程能持有锁

#### Lock 接口（更灵活的锁机制）

```java
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

class LockTicketSeller implements Runnable {
    private int tickets = 100;
    private final Lock lock = new ReentrantLock();  // 创建锁
    
    @Override
    public void run() {
        while (true) {
            lock.lock();  // 加锁
            try {
                if (tickets <= 0) break;
                
                System.out.println(Thread.currentThread().getName() + " 卖出第 " + tickets + " 张票");
                tickets--;
                
                Thread.sleep(10);
            } catch (InterruptedException e) {
                e.printStackTrace();
            } finally {
                lock.unlock();  // 必须在 finally 中释放锁
            }
        }
    }
}

public class LockDemo {
    public static void main(String[] args) {
        LockTicketSeller seller = new LockTicketSeller();
        
        Thread window1 = new Thread(seller, "窗口1");
        Thread window2 = new Thread(seller, "窗口2");
        Thread window3 = new Thread(seller, "窗口3");
        
        window1.start();
        window2.start();
        window3.start();
    }
}
```

**Lock vs synchronized 对比：**

| 特性 | synchronized | Lock |
|-----|-------------|------|
| **实现方式** | JVM 内置关键字 | Java API 接口 |
| **锁释放** | 自动释放 | 手动释放（finally） |
| **灵活性** | 较低 | 高（可中断、超时） |
| **性能** | 较低 | 较高（JDK 6+ 优化后相当） |
| **公平性** | 非公平 | 可选公平/非公平 |
| **使用场景** | 简单同步 | 复杂同步需求 |

### 11.7 线程通信

```java
// 生产者-消费者模型
class Buffer {
    private int data;
    private boolean isEmpty = true;
    
    // 生产者放入数据
    public synchronized void put(int value) {
        while (!isEmpty) {
            try {
                wait();  // 缓冲区满，等待
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        data = value;
        isEmpty = false;
        notifyAll();  // 唤醒等待的消费者
        System.out.println("生产: " + value);
    }
    
    // 消费者取出数据
    public synchronized int get() {
        while (isEmpty) {
            try {
                wait();  // 缓冲区空，等待
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        isEmpty = true;
        notifyAll();  // 唤醒等待的生产者
        System.out.println("消费: " + data);
        return data;
    }
}

class Producer implements Runnable {
    private Buffer buffer;
    
    public Producer(Buffer buffer) {
        this.buffer = buffer;
    }
    
    @Override
    public void run() {
        for (int i = 1; i <= 10; i++) {
            buffer.put(i);
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}

class Consumer implements Runnable {
    private Buffer buffer;
    
    public Consumer(Buffer buffer) {
        this.buffer = buffer;
    }
    
    @Override
    public void run() {
        for (int i = 1; i <= 10; i++) {
            buffer.get();
            try {
                Thread.sleep(150);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}

public class ThreadCommunicationDemo {
    public static void main(String[] args) {
        Buffer buffer = new Buffer();
        
        Thread producer = new Thread(new Producer(buffer));
        Thread consumer = new Thread(new Consumer(buffer));
        
        producer.start();
        consumer.start();
    }
}
```

**线程通信方法：**

| 方法 | 说明 | 所属类 |
|-----|------|-------|
| `wait()` | 线程等待，释放锁 | Object |
| `notify()` | 唤醒一个等待线程 | Object |
| `notifyAll()` | 唤醒所有等待线程 | Object |

**注意：** 这些方法必须在 synchronized 块中使用。

### 11.8 线程池

```java
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class ThreadPoolDemo {
    public static void main(String[] args) {
        // 创建固定大小的线程池
        ExecutorService fixedPool = Executors.newFixedThreadPool(3);
        
        // 提交任务
        for (int i = 1; i <= 10; i++) {
            fixedPool.submit(() -> {
                System.out.println(Thread.currentThread().getName() + " 执行任务");
                try {
                    Thread.sleep(500);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            });
        }
        
        // 关闭线程池
        fixedPool.shutdown();
        try {
            fixedPool.awaitTermination(10, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        
        // 其他线程池类型
        ExecutorService cachedPool = Executors.newCachedThreadPool();  // 缓存线程池
        ExecutorService singlePool = Executors.newSingleThreadExecutor();  // 单线程池
        // ScheduledExecutorService scheduledPool = Executors.newScheduledThreadPool(3);  // 定时线程池
    }
}
```

**线程池优势：**
- 降低资源消耗（复用线程）
- 提高响应速度（任务到达时无需创建线程）
- 便于线程管理（统一分配、调优和监控）

---

## 附录：Java 编码规范

### 命名规范

| 元素 | 规范 | 示例 |
|-----|------|------|
| 包名 | 全小写，点分隔 | `com.example.project` |
| 类名 | 大驼峰（PascalCase） | `UserService`、`OrderDetail` |
| 接口名 | 大驼峰 | `Runnable`、`Serializable` |
| 方法名 | 小驼峰（camelCase） | `getUserName()`、`calculateTotal()` |
| 变量名 | 小驼峰 | `userName`、`orderCount` |
| 常量名 | 全大写 + 下划线 | `MAX_SIZE`、`DEFAULT_TIMEOUT` |
| 枚举值 | 全大写 + 下划线 | `SUCCESS`、`ERROR_CODE` |

### 代码格式

```java
// 1. 缩进：使用 4 个空格（不用 Tab）
// 2. 大括号：K&R 风格（左括号不换行）
if (condition) {
    // 代码
} else {
    // 代码
}

// 3. 空格：运算符两侧加空格
int result = a + b * c;

// 4. 每行代码不超过 120 字符
// 5. 方法之间空一行
// 6. 逻辑代码块之间空一行
```

### 注释规范

```java
/**
 * 用户服务类
 * 
 * <p>提供用户相关的业务操作，包括注册、登录、查询等功能。</p>
 * 
 * @author 作者名
 * @version 1.0
 * @since 2024-01-01
 */
public class UserService {
    
    /**
     * 用户注册
     * 
     * @param username 用户名，不能为空
     * @param password 密码，至少6位
     * @param email 邮箱地址
     * @return 注册成功返回用户ID，失败返回-1
     * @throws IllegalArgumentException 参数不合法时抛出
     */
    public long register(String username, String password, String email) {
        // 单行注释：解释代码逻辑
        if (username == null || username.isEmpty()) {
            return -1;
        }
        
        /* 
         * 多行注释
         * 用于解释复杂的业务逻辑
         */
        return 1;
    }
}
```
