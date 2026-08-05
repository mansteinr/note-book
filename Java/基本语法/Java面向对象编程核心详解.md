# Java 面向对象编程核心详解

> 本文档深入探讨 Java 面向对象编程（OOP）的核心概念，包括封装、继承、多态三大特性，以及抽象类、接口、内部类和对象生命周期等关键机制，并辅以详实的代码示例与设计模式解析。

---

## 目录

1. [面向对象概述](#1-面向对象概述)
2. [封装（Encapsulation）](#2-封装encapsulation)
3. [继承（Inheritance）](#3-继承inheritance)
4. [多态（Polymorphism）](#4-多态polymorphism)
5. [抽象类与接口](#5-抽象类与接口)
6. [内部类](#6-内部类)
7. [对象生命周期与管理](#7-对象生命周期与管理)
8. [访问修饰符与作用域](#8-访问修饰符与作用域)
9. [代码规范与最佳实践](#9-代码规范与最佳实践)
10. [面试高频考点](#10-面试高频考点)

---

## 1. 面向对象概述

### 1.1 什么是面向对象

面向对象编程（Object-Oriented Programming, OOP）是一种编程范式，通过**“对象”**来组织代码。对象是数据（属性/字段）和行为（方法）的集合体。

**核心思想：**
- **万物皆对象**：程序中的所有事物都被建模为对象。
- **抽象**：提取同类事物的共同特征形成“类”（Class）。
- **三大特性**：封装、继承、多态。

### 1.2 类与对象的关系

```java
// 类：对象的蓝图/模板
public class Car {
    String color;
    String brand;
    
    public void start() {
        System.out.println("启动 " + brand + " " + color + "的车");
    }
}

// 对象：类的实例
public class Main {
    public static void main(String[] args) {
        // 创建两个不同的 Car 对象
        Car myCar = new Car();
        myCar.color = "红色";
        myCar.brand = "宝马";
        
        Car yourCar = new Car();
        yourCar.color = "黑色";
        yourCar.brand = "奔驰";
        
        myCar.start();   // 启动 宝马 红色的车
        yourCar.start(); // 启动 奔驰 黑色的车
    }
}
```

**类与对象的关系：**
- 一个类可以创建多个对象
- 每个对象有独立的内存空间（属性独立）
- 方法定义在类中，所有对象共享

---

## 2. 封装（Encapsulation）

### 2.1 封装的概念

封装是将数据（属性）和操作数据的方法绑定在一起，隐藏对象的内部状态，只通过公共方法对外暴露服务。

**封装的核心目的：**
- **保护数据**：防止外部直接修改属性，避免非法值
- **降低耦合**：内部实现变化不影响外部调用
- **提高可维护性**：修改内部逻辑时无需修改调用方

### 2.2 封装的实现

```java
/**
 * 银行账户类 - 演示封装
 */
public class BankAccount {
    // 私有属性：外部无法直接访问
    private String accountNumber;
    private String ownerName;
    private double balance;
    private static double interestRate = 0.025; // 静态属性

    // 构造方法：确保对象创建时状态正确
    public BankAccount(String accountNumber, String ownerName, double initialDeposit) {
        this.accountNumber = accountNumber;
        this.ownerName = ownerName;
        if (initialDeposit >= 0) {
            this.balance = initialDeposit;
        } else {
            System.out.println("初始存款不能为负数，已设为0");
            this.balance = 0;
        }
    }

    // 公共方法：安全地操作私有属性
    // 存款方法
    public void deposit(double amount) {
        if (amount <= 0) {
            System.out.println("存款金额必须为正数");
            return;
        }
        this.balance += amount;
        System.out.println("存入 " + amount + " 元，当前余额：" + this.balance);
    }

    // 取款方法（包含业务规则验证）
    public boolean withdraw(double amount) {
        if (amount <= 0) {
            System.out.println("取款金额必须为正数");
            return false;
        }
        if (amount > this.balance) {
            System.out.println("余额不足");
            return false;
        }
        this.balance -= amount;
        System.out.println("取出 " + amount + " 元，当前余额：" + this.balance);
        return true;
    }

    // 只读的 getter 方法
    public double getBalance() {
        return this.balance;
    }

    public String getAccountNumber() {
        return this.accountNumber;
    }

    public String getOwnerName() {
        return this.ownerName;
    }

    // 静态方法
    public static void setInterestRate(double rate) {
        if (rate >= 0 && rate <= 1) {
            interestRate = rate;
        }
    }

    public static double getInterestRate() {
        return interestRate;
    }

    // 重写 toString 方法
    @Override
    public String toString() {
        return "BankAccount{" +
                "accountNumber='" + accountNumber + '\'' +
                ", ownerName='" + ownerName + '\'' +
                ", balance=" + balance +
                '}';
    }
}

// 使用示例
class EncapsulationDemo {
    public static void main(String[] args) {
        // 创建账户，封装保护初始状态
        BankAccount account = new BankAccount("6222000001", "张三", 1000);
        
        // 通过公共方法安全操作
        account.deposit(500);    // 存入500
        account.withdraw(300);   // 取出300
        account.deposit(-100);   // 会被拒绝
        
        // 读取余额（无法直接修改）
        System.out.println("当前余额：" + account.getBalance());
        System.out.println(account); // 自动调用 toString()
    }
}
```

### 2.3 封装的原则

| 原则 | 说明 | 示例 |
|-----|------|------|
| **最小权限** | 属性一律设为 private | `private double balance;` |
| **受控访问** | 通过 getter/setter 暴露必要接口 | `getBalance()`, `deposit()` |
| **数据验证** | setter 方法中验证数据合法性 | 检查金额是否为负数 |
| **只读属性** | 不提供 setter 方法的属性为只读 | `getAccountNumber()` 无对应 setter |

---

## 3. 继承（Inheritance）

### 3.1 继承的概念

继承是一种机制，允许一个类（子类）获取另一个类（父类）的属性和方法，实现代码复用和层级关系。

**核心概念：**
- **父类/基类**：被继承的类，包含公共属性和方法
- **子类/派生类**：继承父类的类，可以扩展新功能
- **extends 关键字**：用于建立继承关系
- **单一继承**：Java 中一个类只能继承一个父类

### 3.2 继承的实现

```java
/**
 * 动物类 - 父类
 */
public class Animal {
    protected String name;   // protected 允许子类访问
    protected int age;

    // 父类构造方法
    public Animal(String name, int age) {
        this.name = name;
        this.age = age;
        System.out.println("Animal 构造方法被调用");
    }

    // 父类方法
    public void eat() {
        System.out.println(name + " 正在吃东西");
    }

    public void sleep() {
        System.out.println(name + " 正在睡觉");
    }

    public void introduce() {
        System.out.println("我是 " + name + "，今年 " + age + " 岁");
    }
}

/**
 * 狗类 - 继承自 Animal
 */
public class Dog extends Animal {
    private String breed;  // 子类特有属性

    public Dog(String name, int age, String breed) {
        // 调用父类构造方法（必须放在第一行）
        super(name, age);
        this.breed = breed;
        System.out.println("Dog 构造方法被调用");
    }

    // 子类特有方法
    public void bark() {
        System.out.println(name + " 汪汪叫！");
    }

    public void fetch() {
        System.out.println(name + " 去捡球");
    }

    // 方法重写（Override）
    @Override
    public void introduce() {
        super.introduce();  // 调用父类版本
        System.out.println("品种：" + breed);
    }

    @Override
    public String toString() {
        return "Dog{name='" + name + "', age=" + age + ", breed='" + breed + "'}";
    }
}

/**
 * 猫类 - 另一个子类
 */
public class Cat extends Animal {
    private boolean isIndoor;

    public Cat(String name, int age, boolean isIndoor) {
        super(name, age);
        this.isIndoor = isIndoor;
    }

    public void meow() {
        System.out.println(name + " 喵喵叫");
    }

    @Override
    public void introduce() {
        super.introduce();
        System.out.println("类型：" + (isIndoor ? "家猫" : "野猫"));
    }
}

// 使用示例
class InheritanceDemo {
    public static void main(String[] args) {
        Dog dog = new Dog("旺财", 3, "金毛");
        dog.eat();         // 继承自 Animal
        dog.bark();        // Dog 特有
        dog.introduce();   // Dog 重写版本
        
        Cat cat = new Cat("咪咪", 2, true);
        cat.sleep();       // 继承自 Animal
        cat.meow();        // Cat 特有
    }
}
```

### 3.3 构造方法链

```
创建 Dog 对象的过程：
1. 调用 Dog 构造方法
2. 自动调用 super()，进入 Animal 构造方法
3. Animal 构造方法执行，初始化 name 和 age
4. 返回 Dog 构造方法
5. 初始化 breed
6. Dog 对象创建完成
```

**注意事项：**
- 子类构造方法默认第一行有 `super()` 调用
- 如果父类没有无参构造方法，子类必须显式调用 `super(参数)`
- 构造方法不被继承，但可以通过 `super()` 调用

### 3.4 继承的访问限制

| 修饰符 | 同类 | 同包 | 子类 | 不同包 | 说明 |
|--------|------|------|------|--------|------|
| `private` | ✓ | ✗ | ✗ | ✗ | 仅限本类 |
| `default` | ✓ | ✓ | ✗ | ✗ | 默认访问（同包可见） |
| `protected` | ✓ | ✓ | ✓ | ✗ | 保护访问（子类可见） |
| `public` | ✓ | ✓ | ✓ | ✓ | 公共访问 |

---

## 4. 多态（Polymorphism）

### 4.1 多态的概念

多态允许使用统一的接口访问不同类型的对象。通过父类引用指向子类对象，实现"同一接口，不同实现"。

**多态的三种形式：**
1. **方法重写（Override）**：子类重新定义父类方法
2. **方法重载（Overload）**：同一类中同名方法，参数不同
3. **动态绑定**：运行时根据对象实际类型调用对应方法

### 4.2 方法重写 vs 方法重载

```java
public class PolymorphismDemo {
    
    // ===== 方法重载（Overload）=====
    // 同一个类中，方法名相同，参数列表不同
    public int add(int a, int b) {
        return a + b;
    }
    
    public int add(int a, int b, int c) {
        return a + b + c;
    }
    
    public double add(double a, double b) {
        return a + b;
    }
    
    public String add(String a, String b) {
        return a + b;
    }
    
    // ===== 方法重写（Override）=====
    // 子类重新定义父类方法，签名必须一致
    static class Animal {
        public void makeSound() {
            System.out.println("动物发出声音");
        }
    }
    
    static class Dog extends Animal {
        @Override
        public void makeSound() {
            System.out.println("汪汪汪");
        }
    }
    
    static class Cat extends Animal {
        @Override
        public void makeSound() {
            System.out.println("喵喵喵");
        }
    }
    
    // ===== 多态的使用 =====
    public static void playSound(Animal animal) {
        // 同一接口，不同行为
        animal.makeSound();
    }
    
    public static void main(String[] args) {
        // 方法重载演示
        System.out.println(add(1, 2));         // 3
        System.out.println(add(1, 2, 3));      // 6
        System.out.println(add(1.5, 2.5));     // 4.0
        System.out.println(add("Hello", "World")); // HelloWorld
        
        // 多态演示
        Dog dog = new Dog();
        Cat cat = new Cat();
        
        playSound(dog);  // 输出：汪汪汪
        playSound(cat);  // 输出：喵喵喵
        
        // 父类引用指向子类对象
        Animal animal1 = new Dog();
        Animal animal2 = new Cat();
        
        animal1.makeSound(); // 汪汪汪（动态绑定到 Dog 的方法）
        animal2.makeSound(); // 喵喵喵（动态绑定到 Cat 的方法）
    }
}
```

### 4.3 多态的应用场景

**场景一：统一接口处理不同类型**

```java
/**
 * 支付系统 - 多态应用
 */
// 支付接口
interface Payment {
    void pay(double amount);
    String getPaymentMethod();
}

// 支付宝支付
class Alipay implements Payment {
    @Override
    public void pay(double amount) {
        System.out.println("支付宝支付 " + amount + " 元");
    }
    
    @Override
    public String getPaymentMethod() {
        return "支付宝";
    }
}

// 微信支付
class WeChatPay implements Payment {
    @Override
    public void pay(double amount) {
        System.out.println("微信支付 " + amount + " 元");
    }
    
    @Override
    public String getPaymentMethod() {
        return "微信";
    }
}

// 银行卡支付
class BankCard implements Payment {
    private String cardNumber;
    
    public BankCard(String cardNumber) {
        this.cardNumber = cardNumber;
    }
    
    @Override
    public void pay(double amount) {
        System.out.println("银行卡(" + cardNumber + ")支付 " + amount + " 元");
    }
    
    @Override
    public String getPaymentMethod() {
        return "银行卡";
    }
}

// 订单类 - 使用多态
class Order {
    private double totalAmount;
    
    public Order(double totalAmount) {
        this.totalAmount = totalAmount;
    }
    
    // 接受任意 Payment 实现
    public void checkout(Payment payment) {
        System.out.println("订单金额：" + totalAmount + " 元");
        System.out.println("支付方式：" + payment.getPaymentMethod());
        payment.pay(totalAmount);
        System.out.println("支付成功！");
    }
}

// 使用
class PaymentDemo {
    public static void main(String[] args) {
        Order order = new Order(99.99);
        
        // 不同支付方式，统一 checkout 接口
        order.checkout(new Alipay());
        order.checkout(new WeChatPay());
        order.checkout(new BankCard("6222-****-****-1234"));
    }
}
```

**场景二：方法参数支持多种类型**

```java
/**
 * 日志系统 - 多态参数
 */
abstract class Logger {
    public abstract void log(String message);
    
    public void logInfo(String message) {
        log("[INFO] " + message);
    }
    
    public void logError(String message) {
        log("[ERROR] " + message);
    }
}

class ConsoleLogger extends Logger {
    @Override
    public void log(String message) {
        System.out.println(message);
    }
}

class FileLogger extends Logger {
    private String filename;
    
    public FileLogger(String filename) {
        this.filename = filename;
    }
    
    @Override
    public void log(String message) {
        System.out.println("写入文件 " + filename + ": " + message);
        // 实际场景中会写入文件
    }
}

class DatabaseLogger extends Logger {
    @Override
    public void log(String message) {
        System.out.println("存入数据库: " + message);
        // 实际场景中会存入数据库
    }
}

// 使用 - 接受任何 Logger 类型
class Application {
    private Logger logger;
    
    public Application(Logger logger) {
        this.logger = logger;
    }
    
    public void run() {
        logger.logInfo("应用启动");
        // ... 业务逻辑 ...
        logger.logError("发生错误");
    }
}
```

---

## 5. 抽象类与接口

### 5.1 抽象类（Abstract Class）

抽象类是一种不能被实例化的类，用于定义子类必须实现的行为规范。

```java
/**
 * 形状类 - 抽象类
 */
public abstract class Shape {
    protected String color;
    
    public Shape(String color) {
        this.color = color;
    }
    
    // 抽象方法 - 必须由子类实现
    public abstract double calculateArea();
    public abstract double calculatePerimeter();
    public abstract String getType();
    
    // 非抽象方法 - 子类可以直接继承
    public String getColor() {
        return color;
    }
    
    public void displayInfo() {
        System.out.println("类型: " + getType());
        System.out.println("颜色: " + color);
        System.out.println("面积: " + calculateArea());
        System.out.println("周长: " + calculatePerimeter());
    }
}

/**
 * 圆类 - 继承抽象类
 */
public class Circle extends Shape {
    private double radius;
    
    public Circle(String color, double radius) {
        super(color);
        this.radius = radius;
    }
    
    @Override
    public double calculateArea() {
        return Math.PI * radius * radius;
    }
    
    @Override
    public double calculatePerimeter() {
        return 2 * Math.PI * radius;
    }
    
    @Override
    public String getType() {
        return "圆形";
    }
}

/**
 * 矩形类 - 继承抽象类
 */
public class Rectangle extends Shape {
    private double width;
    private double height;
    
    public Rectangle(String color, double width, double height) {
        super(color);
        this.width = width;
        this.height = height;
    }
    
    @Override
    public double calculateArea() {
        return width * height;
    }
    
    @Override
    public double calculatePerimeter() {
        return 2 * (width + height);
    }
    
    @Override
    public String getType() {
        return "矩形";
    }
}

// 使用
class AbstractDemo {
    public static void main(String[] args) {
        Shape circle = new Circle("红色", 5.0);
        Shape rectangle = new Rectangle("蓝色", 4.0, 3.0);
        
        // 多态调用
        circle.displayInfo();
        rectangle.displayInfo();
        
        // Shape shape = new Shape("黑色"); // 错误：抽象类不能实例化
    }
}
```

**抽象类的特点：**
- 使用 `abstract` 关键字修饰
- 可以包含抽象方法和具体方法
- 可以有构造方法和字段
- 子类必须实现所有抽象方法（除非子类也是抽象类）
- 不能被直接实例化

### 5.2 接口（Interface）

接口是行为的契约，定义了类应该做什么，但不关心如何做。

```java
/**
 * 可飞行接口
 */
public interface Flyable {
    void fly();
    double getMaxAltitude();
}

/**
 * 可游水接口
 */
public interface Swimmable {
    void swim();
    double getMaxDepth();
}

/**
 * 可奔跑接口
 */
public interface Runnable {
    void run();
    double getMaxSpeed();
}

/**
 * 鸭子类 - 实现多个接口
 */
public class Duck implements Flyable, Swimmable {
    private String name;
    
    public Duck(String name) {
        this.name = name;
    }
    
    @Override
    public void fly() {
        System.out.println(name + " 在飞");
    }
    
    @Override
    public double getMaxAltitude() {
        return 100.0; // 米
    }
    
    @Override
    public void swim() {
        System.out.println(name + " 在游泳");
    }
    
    @Override
    public double getMaxDepth() {
        return 5.0; // 米
    }
}

/**
 * 鹰类 - 实现飞行接口
 */
public class Eagle implements Flyable {
    @Override
    public void fly() {
        System.out.println("鹰在高飞");
    }
    
    @Override
    public double getMaxAltitude() {
        return 5000.0; // 米
    }
}

/**
 * 机器人 - 实现奔跑接口
 */
public class Robot implements Runnable {
    @Override
    public void run() {
        System.out.println("机器人在奔跑");
    }
    
    @Override
    public double getMaxSpeed() {
        return 30.0; // km/h
    }
}

/**
 * 接口的默认方法和静态方法（Java 8+）
 */
public interface Vehicle {
    void start();
    void stop();
    
    // 默认方法 - 接口提供默认实现
    default void horn() {
        System.out.println("鸣笛：嘀嘀");
    }
    
    default String getDescription() {
        return "交通工具";
    }
    
    // 静态方法 - 接口工具方法
    static Vehicle createElectricVehicle() {
        return new ElectricCar();
    }
}

class ElectricCar implements Vehicle {
    @Override
    public void start() {
        System.out.println("电动车启动");
    }
    
    @Override
    public void stop() {
        System.out.println("电动车停止");
    }
    
    // 可以选择性覆盖默认方法
    @Override
    public void horn() {
        System.out.println("电动车鸣笛：嗡嗡");
    }
}

// 使用
class InterfaceDemo {
    public static void main(String[] args) {
        Duck duck = new Duck("小鸭子");
        duck.fly();
        duck.swim();
        
        Eagle eagle = new Eagle();
        eagle.fly();
        System.out.println("最大飞行高度：" + eagle.getMaxAltitude() + "米");
        
        // 接口多态
        Flyable[] flyers = {duck, eagle};
        for (Flyable flyer : flyers) {
            flyer.fly();
        }
        
        // Java 8+ 特性
        Vehicle car = Vehicle.createElectricVehicle();
        car.start();
        car.horn();
    }
}
```

**接口的特点：**
- 使用 `interface` 关键字定义
- 默认方法访问修饰符为 `public`
- Java 8+ 支持 `default` 方法和 `static` 方法
- Java 9+ 支持 `private` 方法
- 一个类可以实现多个接口（弥补单一继承的不足）
- 接口本身不能实例化

### 5.3 抽象类 vs 接口对比

| 特性 | 抽象类 | 接口 |
|-----|-------|------|
| 关键字 | `abstract class` | `interface` |
| 实例化 | 不能 | 不能 |
| 构造方法 | 可以有 | 不能有 |
| 成员变量 | 任意类型 | 只能是 `static final` |
| 方法实现 | 可有具体方法 | Java 8+ 可有 default/static 方法 |
| 继承数量 | 单一继承 | 可实现多个接口 |
| 设计目的 | "是什么"（is-a） | "能做什么"（can-do） |

---

## 6. 内部类

### 6.1 内部类的类型

```java
/**
 * 内部类类型演示
 */
public class OuterClass {
    private String outerField = "外部类字段";
    private static String staticField = "静态字段";
    
    /**
     * 成员内部类
     */
    public class MemberInner {
        private String innerField = "内部类字段";
        
        public void display() {
            // 可以直接访问外部类的所有成员
            System.out.println("访问外部类字段: " + outerField);
            System.out.println("访问内部类字段: " + innerField);
        }
    }
    
    /**
     * 静态内部类
     */
    public static class StaticInner {
        private String staticInnerField = "静态内部类字段";
        
        public void display() {
            // 只能访问外部类的静态成员
            System.out.println("访问外部类静态字段: " + staticField);
            System.out.println("访问静态内部类字段: " + staticInnerField);
        }
        
        // 静态内部类可以有静态方法
        public static void staticMethod() {
            System.out.println("静态内部类的静态方法");
        }
    }
    
    /**
     * 方法内部类
     */
    public void methodWithInner() {
        final String localVar = "局部变量";
        
        class LocalInner {
            public void display() {
                // 只能访问 final 或 effectively final 的局部变量
                System.out.println("访问局部变量: " + localVar);
                System.out.println("访问外部类字段: " + outerField);
            }
        }
        
        LocalInner local = new LocalInner();
        local.display();
    }
    
    /**
     * 匿名内部类
     */
    public void anonymousClassDemo() {
        // 匿名内部类实现接口
        Runnable runnable = new Runnable() {
            @Override
            public void run() {
                System.out.println("匿名内部类: 实现 Runnable 接口");
                System.out.println("外部类字段: " + outerField);
            }
        };
        
        runnable.run();
        
        // 匿名内部类继承父类
        Thread thread = new Thread() {
            @Override
            public void run() {
                System.out.println("匿名内部类: 继承 Thread 类");
            }
        };
        
        thread.start();
    }
    
    // 外部类方法
    public void test() {
        // 创建成员内部类实例
        MemberInner member = new MemberInner();
        member.display();
        
        // 创建静态内部类实例
        StaticInner staticInner = new StaticInner();
        staticInner.display();
        StaticInner.staticMethod();
        
        // 调用包含方法内部类的方法
        methodWithInner();
        
        // 调用匿名内部类演示
        anonymousClassDemo();
    }
    
    public static void main(String[] args) {
        OuterClass outer = new OuterClass();
        outer.test();
    }
}
```

### 6.2 内部类的应用场景

**场景一：事件处理器**

```java
public class EventHandlerDemo {
    private String eventMessage;
    
    public void setupEventHandlers() {
        // Java 8+ 使用 Lambda 表达式（实际是匿名内部类的语法糖）
        Runnable onClickHandler = () -> {
            eventMessage = "按钮被点击";
            System.out.println(eventMessage);
        };
        
        // 传统方式：匿名内部类
        Runnable oldStyleHandler = new Runnable() {
            @Override
            public void run() {
                eventMessage = "按钮被点击（传统方式）";
                System.out.println(eventMessage);
            }
        };
    }
}
```

**场景二：迭代器实现**

```java
public class CustomList<T> {
    private Object[] elements;
    private int size;
    
    public CustomList() {
        elements = new Object[10];
        size = 0;
    }
    
    public void add(T element) {
        elements[size++] = element;
    }
    
    // 返回内部类实现的迭代器
    public Iterator<T> iterator() {
        return new ListIterator();  // 成员内部类
    }
    
    /**
     * 成员内部类实现迭代器
     */
    private class ListIterator implements Iterator<T> {
        private int currentIndex = 0;
        
        @Override
        public boolean hasNext() {
            return currentIndex < size;
        }
        
        @Override
        @SuppressWarnings("unchecked")
        public T next() {
            if (!hasNext()) {
                throw new NoSuchElementException();
            }
            return (T) elements[currentIndex++];
        }
    }
}
```

---

## 7. 对象生命周期与管理

### 7.1 对象的创建过程

```java
public class ObjectLifecycle {
    
    // 静态代码块 - 类加载时执行一次
    static {
        System.out.println("1. 静态代码块执行");
    }
    
    // 静态成员初始化
    private static String staticField = initializeStatic();
    
    private static String initializeStatic() {
        System.out.println("2. 静态成员初始化");
        return "静态值";
    }
    
    // 实例代码块 - 每次创建对象时执行
    {
        System.out.println("3. 实例代码块执行");
    }
    
    // 实例成员初始化
    private String instanceField = initializeInstance();
    
    private String initializeInstance() {
        System.out.println("4. 实例成员初始化");
        return "实例值";
    }
    
    // 构造方法
    public ObjectLifecycle() {
        System.out.println("5. 构造方法执行");
    }
    
    public static void main(String[] args) {
        System.out.println("--- 创建第一个对象 ---");
        ObjectLifecycle obj1 = new ObjectLifecycle();
        
        System.out.println("\n--- 创建第二个对象 ---");
        ObjectLifecycle obj2 = new ObjectLifecycle();
    }
}
```

**输出顺序：**
```
--- 创建第一个对象 ---
1. 静态代码块执行
2. 静态成员初始化
3. 实例代码块执行
4. 实例成员初始化
5. 构造方法执行

--- 创建第二个对象 ---
3. 实例代码块执行
4. 实例成员初始化
5. 构造方法执行
```

### 7.2 垃圾回收与对象销毁

```java
public class GarbageCollectionDemo {
    
    @Override
    protected void finalize() throws Throwable {
        // 最终化方法 - 在垃圾回收前调用
        // 注意：不保证被调用，不应依赖此方法
        System.out.println("对象被垃圾回收: " + this);
    }
    
    public static void main(String[] args) {
        // 创建对象
        Object obj1 = new Object();
        Object obj2 = new Object();
        
        // 使 obj1 符合垃圾回收条件
        obj1 = null;
        
        // 建议进行垃圾回收（不保证立即执行）
        System.gc();
        System.runFinalization();
        
        // obj2 仍在使用，不会被回收
        System.out.println("obj2 引用的对象仍存在: " + obj2);
    }
}
```

**对象被回收的条件：**
1. 对象没有任何引用指向它
2. 程序结束前仍存在，但 JVM 即将终止
3. 在方法作用域内，方法结束后局部变量对象可被回收

### 7.3 finalize 方法的使用

```java
/**
 * finalize 方法的正确使用（已过时，仅作了解）
 */
@Deprecated
public class ResourceManager {
    private boolean closed = false;
    private String resourceName;
    
    public ResourceManager(String name) {
        this.resourceName = name;
    }
    
    public void close() {
        if (!closed) {
            // 释放资源
            System.out.println("释放资源: " + resourceName);
            closed = true;
        }
    }
    
    @Override
    protected void finalize() throws Throwable {
        // 作为安全网：如果忘记调用 close()
        // 但不能保证此方法被及时调用
        if (!closed) {
            System.out.println("警告：资源 " + resourceName + " 未正确关闭");
            close();
        }
        super.finalize();
    }
}
```

**最佳实践：**
- 不要依赖 `finalize()` 方法
- 使用 `try-with-resources` 自动关闭资源
- 实现 `AutoCloseable` 接口

---

## 8. 访问修饰符与作用域

### 8.1 四种访问修饰符

```java
/**
 * 访问修饰符演示
 */

// 类的访问修饰符：public 或 default
public class AccessControl {
    // 私有成员 - 仅本类可见
    private String privateField = "私有字段";
    
    // 默认成员 - 同包可见
    String defaultField = "默认字段";
    
    // 保护成员 - 同包和子类可见
    protected String protectedField = "保护字段";
    
    // 公共成员 - 所有类可见
    public String publicField = "公共字段";
    
    // 私有方法
    private void privateMethod() {
        System.out.println("私有方法");
    }
    
    // 默认方法
    void defaultMethod() {
        System.out.println("默认方法");
    }
    
    // 保护方法
    protected void protectedMethod() {
        System.out.println("保护方法");
    }
    
    // 公共方法
    public void publicMethod() {
        System.out.println("公共方法");
    }
}

// 同包的另一个类
class SamePackageClass {
    public void testAccess() {
        AccessControl obj = new AccessControl();
        
        // obj.privateField    // 错误：私有成员不可见
        // obj.privateMethod() // 错误：私有方法不可见
        
        obj.defaultField;     // 正确：默认成员可见
        obj.defaultMethod(); // 正确：默认方法可见
        
        obj.protectedField;     // 正确：保护成员可见
        obj.protectedMethod(); // 正确：保护方法可见
        
        obj.publicField;     // 正确：公共成员可见
        obj.publicMethod(); // 正确：公共方法可见
    }
}
```

### 8.2 修饰符使用场景

| 场景 | 推荐修饰符 | 原因 |
|-----|-----------|------|
| 类的属性 | `private` | 实现封装，通过 getter/setter 访问 |
| 类的方法 | 根据用途 | 辅助方法用 `private`，对外接口用 `public` |
| 常量 | `public static final` | 公共常量 |
| 工具方法 | `public static` | 无状态的公共工具 |
| 继承扩展点 | `protected` | 允许子类访问但不对外暴露 |

---

## 9. 代码规范与最佳实践

### 9.1 命名规范

```java
/**
 * 命名规范示例
 */
public class NamingConventions {
    
    // 类名：大驼峰（PascalCase）
    public class CustomerService { }
    
    // 方法名：小驼峰（camelCase），动词开头
    public String getCustomerName() { }
    public void processOrder() { }
    public boolean isValid() { }
    
    // 变量名：小驼峰
    private String customerName;
    private int orderCount;
    
    // 常量：全大写，下划线分隔
    public static final int MAX_RETRY_COUNT = 3;
    public static final String DEFAULT_DATE_FORMAT = "yyyy-MM-dd";
    
    // 包名：全小写，点分隔
    // com.example.service
    
    // 接口名：通常以形容词或名词
    public interface Comparable<T> { }
    public interface Runnable { }
    
    // 抽象类：通常以 Abstract 开头
    public abstract class AbstractProcessor { }
    
    // 异常类：以 Exception 结尾
    public class BusinessException extends Exception { }
    
    // 测试类：以 Test 结尾
    public class CustomerServiceTest { }
    
    // 集合类变量：复数形式
    private List<String> customers;
    private Map<String, Integer> scores;
}
```

### 9.2 设计原则

**单一职责原则（SRP）：**
```java
// ❌ 错误：一个类做太多事
public class UserManager {
    public void registerUser() { /* 注册 */ }
    public void sendEmail() { /* 发邮件 */ }
    public void saveToDatabase() { /* 存数据库 */ }
    public void generateReport() { /* 生成报表 */ }
}

// ✅ 正确：职责分离
public class UserService {
    private EmailService emailService;
    private UserRepository userRepository;
    
    public void registerUser(User user) {
        userRepository.save(user);
        emailService.sendWelcomeEmail(user.getEmail());
    }
}
```

**开放封闭原则（OCP）：**
```java
// ❌ 错误：每增加一种支付方式都要修改原有代码
public class PaymentProcessor {
    public void processPayment(Order order, String type) {
        if ("alipay".equals(type)) { /* 支付宝逻辑 */ }
        else if ("wechat".equals(type)) { /* 微信逻辑 */ }
        else if ("bank".equals(type)) { /* 银行卡逻辑 */ }
    }
}

// ✅ 正确：对扩展开放，对修改封闭
public interface PaymentStrategy {
    void pay(Order order);
}

public class AlipayPayment implements PaymentStrategy { /* ... */ }
public class WechatPayment implements PaymentStrategy { /* ... */ }

public class PaymentProcessor {
    public void processPayment(Order order, PaymentStrategy strategy) {
        strategy.pay(order);
    }
}
```

### 9.3 代码示例：完整的面向对象设计

```java
/**
 * 图书管理系统 - 完整 OOP 示例
 */

// 基类：图书
public abstract class Book {
    protected String isbn;
    protected String title;
    protected String author;
    protected boolean isAvailable;
    
    public Book(String isbn, String title, String author) {
        this.isbn = isbn;
        this.title = title;
        this.author = author;
        this.isAvailable = true;
    }
    
    public abstract String getCategory();
    public abstract int getBorrowDays();
    
    public boolean borrow() {
        if (isAvailable) {
            isAvailable = false;
            return true;
        }
        return false;
    }
    
    public void returnBook() {
        isAvailable = true;
    }
    
    // getter/setter
    public String getIsbn() { return isbn; }
    public String getTitle() { return title; }
    public String getAuthor() { return author; }
    public boolean isAvailable() { return isAvailable; }
    
    @Override
    public String toString() {
        return String.format("[%s] %s - %s (%s)", getCategory(), title, author, isAvailable ? "可借" : "借出");
    }
}

// 图书类别
public class FictionBook extends Book {
    public FictionBook(String isbn, String title, String author) {
        super(isbn, title, author);
    }
    
    @Override
    public String getCategory() {
        return "小说";
    }
    
    @Override
    public int getBorrowDays() {
        return 30;
    }
}

public class Textbook extends Book {
    public Textbook(String isbn, String title, String author) {
        super(isbn, title, author);
    }
    
    @Override
    public String getCategory() {
        return "教材";
    }
    
    @Override
    public int getBorrowDays() {
        return 14;
    }
}

// 图书馆接口
public interface Library {
    void addBook(Book book);
    Book findByIsbn(String isbn);
    boolean borrowBook(String isbn);
    boolean returnBook(String isbn);
    List<Book> getAvailableBooks();
}

// 图书馆实现
public class LibrarySystem implements Library {
    private List<Book> books = new ArrayList<>();
    
    @Override
    public void addBook(Book book) {
        books.add(book);
        System.out.println("添加图书：" + book);
    }
    
    @Override
    public Book findByIsbn(String isbn) {
        for (Book book : books) {
            if (book.getIsbn().equals(isbn)) {
                return book;
            }
        }
        return null;
    }
    
    @Override
    public boolean borrowBook(String isbn) {
        Book book = findByIsbn(isbn);
        if (book != null && book.borrow()) {
            System.out.println("借阅成功：" + book.getTitle());
            return true;
        }
        System.out.println("借阅失败：" + (book == null ? "图书不存在" : "已被借出"));
        return false;
    }
    
    @Override
    public boolean returnBook(String isbn) {
        Book book = findByIsbn(isbn);
        if (book != null && !book.isAvailable()) {
            book.returnBook();
            System.out.println("归还成功：" + book.getTitle());
            return true;
        }
        System.out.println("归还失败");
        return false;
    }
    
    @Override
    public List<Book> getAvailableBooks() {
        List<Book> available = new ArrayList<>();
        for (Book book : books) {
            if (book.isAvailable()) {
                available.add(book);
            }
        }
        return available;
    }
    
    // 统计方法
    public void printStatistics() {
        int total = books.size();
        int available = getAvailableBooks().size();
        System.out.println("========== 图书馆统计 ==========");
        System.out.println("图书总数：" + total);
        System.out.println("可借阅：" + available);
        System.out.println("已借出：" + (total - available));
        System.out.println("================================");
    }
}

// 使用示例
class LibraryDemo {
    public static void main(String[] args) {
        LibrarySystem library = new LibrarySystem();
        
        // 添加图书
        library.addBook(new FictionBook("978-001", "三体", "刘慈欣"));
        library.addBook(new FictionBook("978-002", "活着", "余华"));
        library.addBook(new Textbook("978-003", "数据结构", "严蔚敏"));
        library.addBook(new Textbook("978-004", "计算机网络", "谢希仁"));
        
        // 借阅
        System.out.println("\n========== 借阅操作 ==========");
        library.borrowBook("978-001");
        library.borrowBook("978-003");
        library.borrowBook("978-001"); // 再次尝试借阅同一本书
        
        // 归还
        System.out.println("\n========== 归还操作 ==========");
        library.returnBook("978-001");
        
        // 统计
        library.printStatistics();
        
        // 查看可借图书
        System.out.println("\n========== 可借阅图书 ==========");
        for (Book book : library.getAvailableBooks()) {
            System.out.println(book);
        }
    }
}
```

---

## 10. 面试高频考点

### 10.1 三大特性相关问题

**Q1: Java 中继承的特点是什么？**
- 单一继承：一个类只能继承一个父类
- 可多层继承：形成继承链
- 子类继承父类的非私有成员
- 构造方法不被继承，但可通过 `super()` 调用
- 子类可以扩展父类功能

**Q2: 方法重写的规则是什么？**
- 方法签名必须完全相同（方法名、参数列表、返回值类型）
- 访问修饰符不能比父类更严格
- 抛出异常不能比父类更宽泛
- `@Override` 注解建议使用
- 静态方法不存在重写，只有隐藏

**Q3: 多态的实现条件是什么？**
1. 必须有继承或实现接口
2. 必须有方法重写
3. 父类引用指向子类对象
4. 运行时动态绑定到子类方法

### 10.2 抽象类与接口相关问题

**Q4: 抽象类和接口的区别？**
参考本文 [5.3 章节](#53-抽象类-vs-接口对比)

**Q5: 为什么 Java 中接口比抽象类更常用？**
- 接口可以多实现，扩展更灵活
- 接口定义行为契约，更符合面向对象设计
- 便于使用策略模式、装饰器模式等设计模式
- Java 8+ 支持默认方法，接口功能增强

### 10.3 封装相关问题

**Q6: 封装的好处是什么？**
- 保护内部数据，防止非法修改
- 降低类之间的耦合度
- 提高代码可维护性
- 隐藏实现细节，对外只暴露必要接口

**Q7: 什么是 Bean 规范？**
- 所有属性私有化（private）
- 提供公共的 getter/setter 方法
- 实现 `Serializable` 接口
- 提供无参构造方法
- 属性名与 getter/setter 方法名对应

---

## 附录：核心概念速查表

| 概念 | 关键字 | 说明 |
|-----|-------|------|
| 封装 | `private`, `public`, `protected` | 隐藏内部实现 |
| 继承 | `extends` | 获取父类属性和方法 |
| 多态 | 父类引用指向子类对象 | 统一接口，不同实现 |
| 抽象类 | `abstract class` | 定义模板，子类实现 |
| 接口 | `interface` | 定义行为契约 |
| 内部类 | 嵌套在类中的类 | 可访问外部类成员 |
| 方法重写 | `@Override` | 子类重新定义父类方法 |
| 方法重载 | 同名不同参数 | 同类中同名方法的不同版本 |
| 静态成员 | `static` | 属于类，不属于对象 |
| 实例成员 | 无 `static` | 属于对象，每个对象独立 |

---

**文档版本：** 1.0  
**最后更新：** 2026-08-05  
**适用 Java 版本：** Java 8+ / 11+ / 21+
