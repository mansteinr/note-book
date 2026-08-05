# Java 输入输出流详解

## 1. IO流概述

### 1.1 什么是IO

IO是指Input/Output，即输入和输出。以内存为中心：

- **Input**：从外部读入数据到内存（如：从磁盘读取文件、从网络接收数据）
- **Output**：将数据从内存输出到外部（如：写入文件、发送网络数据）

代码在内存中运行，数据必须读到内存才能处理，最终表示形式为 `byte[]`、`String` 等。

### 1.2 IO流分类

Java IO流按数据单位分为两大类：

| 类型 | 基类 | 数据单位 | 适用场景 |
|------|------|----------|----------|
| 字节流 | `InputStream` / `OutputStream` | `byte`（字节） | 二进制数据（图片、视频、压缩包等） |
| 字符流 | `Reader` / `Writer` | `char`（字符） | 文本数据（自动处理字符编码） |

**IO流特点**：单向流动，数据像自来水一样在水管中流动。

### 1.3 同步与异步IO

- **同步IO**：读写时代码必须等待数据返回后才能继续执行。`java.io` 包提供同步IO。
- **异步IO**：读写时仅发出请求，立即执行后续代码。`java.nio` 包提供异步IO（NIO）。

---

## 2. InputStream 字节输入流

### 2.1 核心方法

`InputStream` 是所有输入流的抽象基类（位于 `java.io` 包）。

```java
public abstract int read() throws IOException;
```

- 读取流的下一个字节，返回 `0~255` 的 `int` 值
- 读到末尾返回 `-1`

### 2.2 缓冲区读取

```java
public int read(byte[] b) throws IOException;
public int read(byte[] b, int off, int len) throws IOException;
```

- 一次读取多个字节到缓冲区
- 返回实际读取的字节数，`-1` 表示结束

### 2.3 文件输入示例

```java
public void readFile() throws IOException {
    try (InputStream input = new FileInputStream("src/readme.txt")) {
        byte[] buffer = new byte[1024];
        int n;
        while ((n = input.read(buffer)) != -1) {
            System.out.println("读取 " + n + " 字节");
        }
    }
}
```

### 2.4 常用实现类

| 实现类 | 说明 |
|--------|------|
| `FileInputStream` | 从文件读取数据 |
| `ByteArrayInputStream` | 在内存中模拟输入流（常用于测试） |
| `BufferedInputStream` | 带缓冲的输入流 |
| `DataInputStream` | 读取基本数据类型 |

**测试技巧**：使用 `ByteArrayInputStream` 在不依赖真实文件的情况下测试代码。

```java
byte[] data = {72, 101, 108, 108, 111, 33};
try (InputStream input = new ByteArrayInputStream(data)) {
    String s = readAsString(input);
    System.out.println(s);  // Hello!
}
```

### 2.5 阻塞特性

`read()` 方法是**阻塞的**：必须等方法返回后才能执行下一行代码。这是IO操作的基本特征。

---

## 3. OutputStream 字节输出流

### 3.1 核心方法

`OutputStream` 是所有输出流的抽象基类。

```java
public abstract void write(int b) throws IOException;
```

- 写入一个字节到输出流
- 参数为 `int`，但只写入低8位（相当于 `b & 0xff`）

### 3.2 核心方法：flush()

```java
public void flush() throws IOException;
```

将缓冲区内容强制输出到目的地。

**为什么需要flush？**
- 操作系统将输出数据先存放在内存缓冲区
- 缓冲区满后才一次性写入磁盘/网络
- 聊天软件等场景需要立即发送消息，必须手动调用 `flush()`

### 3.3 文件输出示例

```java
public void writeFile() throws IOException {
    try (OutputStream output = new FileOutputStream("out/readme.txt")) {
        output.write("Hello".getBytes("UTF-8"));
        output.flush();  // 可选，close() 会自动调用
    }
}
```

### 3.4 常用实现类

| 实现类 | 说明 |
|--------|------|
| `FileOutputStream` | 写入文件 |
| `ByteArrayOutputStream` | 在内存中模拟输出流 |
| `BufferedOutputStream` | 带缓冲的输出流 |
| `DataOutputStream` | 写入基本数据类型 |

```java
// 使用 ByteArrayOutputStream 收集数据
try (ByteArrayOutputStream output = new ByteArrayOutputStream()) {
    output.write("Hello ".getBytes("UTF-8"));
    output.write("World!".getBytes("UTF-8"));
    byte[] result = output.toByteArray();
    System.out.println(new String(result, "UTF-8"));
}
```

---

## 4. Reader/Writer 字符流

### 4.1 为什么需要字符流

直接使用字节流处理文本时，需要手动处理字符编码。`Reader` 和 `Writer` 本质上是自动编解码的 `InputStream`/`OutputStream`。

```java
// 使用 Writer 写入中文
try (Writer writer = new FileWriter("output.txt", StandardCharsets.UTF_8)) {
    writer.write("Hello 你好");
}

// 使用 Reader 读取文本
try (Reader reader = new FileReader("input.txt", StandardCharsets.UTF_8)) {
    char[] buffer = new char[1024];
    int n;
    StringBuilder sb = new StringBuilder();
    while ((n = reader.read(buffer)) != -1) {
        sb.append(buffer, 0, n);
    }
    System.out.println(sb);
}
```

### 4.2 常用实现类

| 类 | 说明 |
|----|------|
| `FileReader` / `FileWriter` | 文件字符流 |
| `BufferedReader` / `BufferedWriter` | 带缓冲的字符流 |
| `InputStreamReader` / `OutputStreamWriter` | 字节流转字符流的桥梁 |
| `PrintWriter` | 格式化输出（支持println） |

### 4.3 BufferedReader 读取行

```java
try (BufferedReader reader = new BufferedReader(new FileReader("logs.txt"))) {
    String line;
    while ((line = reader.readLine()) != null) {
        System.out.println(line);
    }
}
```

### 4.4 PrintWriter 格式化输出

```java
try (PrintWriter writer = new PrintWriter(new FileWriter("output.txt"))) {
    writer.println("第一行");
    writer.printf("姓名：%s, 年龄：%d%n", "张三", 25);
}
```

---

## 5. File 对象

### 5.1 创建 File 对象

`File` 类位于 `java.io` 包，代表文件或目录。

```java
// 绝对路径
File file = new File("C:\\Windows\\notepad.exe");

// 相对路径
File file = new File("src/data.txt");

// 使用路径组件
File file = new File("src", "data.txt");
```

**注意**：创建 `File` 对象本身不涉及IO操作，只有调用具体方法时才会访问磁盘。

### 5.2 路径表示

```java
File file = new File("..\\src\\data.txt");

file.getPath();           // 返回构造时的路径
file.getAbsolutePath();   // 返回绝对路径
file.getCanonicalPath();  // 返回规范路径（解析 . 和 ..）
File.separator            // 系统路径分隔符（Windows: \, Linux: /）
```

### 5.3 文件属性判断

```java
File file = new File("data.txt");

file.isFile();          // 是否是文件
file.isDirectory();     // 是否是目录
file.exists();          // 是否存在
file.canRead();         // 是否可读
file.canWrite();        // 是否可写
file.length();          // 文件大小（字节）
file.lastModified();    // 最后修改时间
```

### 5.4 创建与删除

```java
// 创建文件
File file = new File("new.txt");
if (file.createNewFile()) {
    System.out.println("文件创建成功");
}

// 创建临时文件
File tempFile = File.createTempFile("tmp-", ".txt");
tempFile.deleteOnExit();  // JVM退出时自动删除

// 删除文件
file.delete();

// 创建目录
File dir = new File("mydir");
dir.mkdir();    // 创建单级目录
dir.mkdirs();   // 创建多级目录（含父目录）
```

### 5.5 遍历目录

```java
File dir = new File("C:\\Users\\Documents");

// 列出所有文件
File[] files = dir.listFiles();

// 使用过滤器列出指定类型
File[] txtFiles = dir.listFiles(new FilenameFilter() {
    @Override
    public boolean accept(File d, String name) {
        return name.endsWith(".txt");
    }
});

// 使用 Lambda 表达式（Java 8+）
File[] javaFiles = dir.listFiles((d, name) -> name.endsWith(".java"));
```

### 5.6 Path 对象（NIO.2）

`java.nio.file.Path` 提供更现代的文件操作API：

```java
Path path = Paths.get("src", "main", "java");
Path absolutePath = path.toAbsolutePath();
Path normalizedPath = absolutePath.normalize();

// Path 与 File 互转
File file = path.toFile();
Path path2 = file.toPath();

// 遍历目录
try (DirectoryStream<Path> stream = Files.newDirectoryStream(Paths.get("."))) {
    for (Path entry : stream) {
        System.out.println(entry.getFileName());
    }
}
```

---

## 6. try-with-resources 资源管理

### 6.1 为什么需要

IO操作涉及系统资源（文件句柄、网络连接），必须在使用后释放。若不关闭，会导致资源泄漏。

### 6.2 传统方式（try-finally）

```java
InputStream input = null;
try {
    input = new FileInputStream("data.txt");
    int n;
    while ((n = input.read()) != -1) {
        System.out.println(n);
    }
} finally {
    if (input != null) {
        try {
            input.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

### 6.3 推荐方式（try-with-resources）

Java 7 引入自动资源管理，实现 `AutoCloseable` 接口的对象可自动关闭。

```java
try (InputStream input = new FileInputStream("data.txt")) {
    int n;
    while ((n = input.read()) != -1) {
        System.out.println(n);
    }
}  // 编译器自动调用 input.close()
```

### 6.4 多资源管理

```java
try (InputStream input = new FileInputStream("source.txt");
     OutputStream output = new FileOutputStream("target.txt")) {
    input.transferTo(output);  // Java 9+ 提供的便捷方法
}
```

### 6.5 自定义 AutoCloseable

```java
public class MyResource implements AutoCloseable {
    @Override
    public void close() throws Exception {
        // 资源释放逻辑
    }
}

try (MyResource resource = new MyResource()) {
    // 使用资源
}
```

---

## 7. Filter 模式与装饰器

### 7.1 装饰器模式结构

Java IO 使用装饰器（Decorator）模式，通过包装器为流增加功能：

```
基础流：FileInputStream / FileOutputStream
  ↓ 装饰
缓冲流：BufferedInputStream / BufferedOutputStream
  ↓ 装饰
数据流：DataInputStream / DataOutputStream
```

### 7.2 缓冲流

```java
// 带缓冲读取，性能更优
try (BufferedInputStream bis = new BufferedInputStream(
        new FileInputStream("large_file.dat"))) {
    byte[] buffer = new byte[8192];
    int n;
    while ((n = bis.read(buffer)) != -1) {
        // 处理数据
    }
}
```

### 7.3 数据流

```java
// 写入基本数据类型
try (DataOutputStream dos = new DataOutputStream(
        new FileOutputStream("data.bin"))) {
    dos.writeInt(42);
    dos.writeDouble(3.14159);
    dos.writeUTF("Hello");
}

// 读取基本数据类型
try (DataInputStream dis = new DataInputStream(
        new FileInputStream("data.bin"))) {
    int num = dis.readInt();
    double pi = dis.readDouble();
    String msg = dis.readUTF();
}
```

### 7.4 对象流（序列化）

```java
// 序列化对象
try (ObjectOutputStream oos = new ObjectOutputStream(
        new FileOutputStream("person.ser"))) {
    Person person = new Person("张三", 25);
    oos.writeObject(person);
}

// 反序列化对象
try (ObjectInputStream ois = new ObjectInputStream(
        new FileInputStream("person.ser"))) {
    Person person = (Person) ois.readObject();
}

// 实现 Serializable 接口
public class Person implements Serializable {
    private String name;
    private int age;
}
```

---

## 8. 综合应用示例

### 8.1 文件复制

```java
public class FileCopy {
    public static void copy(String sourcePath, String targetPath) throws IOException {
        try (InputStream input = new FileInputStream(sourcePath);
             OutputStream output = new FileOutputStream(targetPath)) {
            byte[] buffer = new byte[8192];
            int n;
            while ((n = input.read(buffer)) != -1) {
                output.write(buffer, 0, n);
            }
        }
    }

    public static void main(String[] args) {
        try {
            copy(args[0], args[1]);
            System.out.println("文件复制成功");
        } catch (IOException e) {
            System.err.println("复制失败: " + e.getMessage());
        }
    }
}
```

### 8.2 文本文件处理

```java
public class TextProcessor {
    // 读取整个文本文件
    public static String readAll(String path) throws IOException {
        try (BufferedReader reader = new BufferedReader(
                new FileReader(path, StandardCharsets.UTF_8))) {
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                if (sb.length() > 0) {
                    sb.append(System.lineSeparator());
                }
                sb.append(line);
            }
            return sb.toString();
        }
    }

    // 写入文本文件
    public static void writeAll(String path, String content) throws IOException {
        try (PrintWriter writer = new PrintWriter(
                new FileWriter(path, StandardCharsets.UTF_8))) {
            writer.print(content);
        }
    }

    // 统计文件行数
    public static int countLines(String path) throws IOException {
        try (BufferedReader reader = new BufferedReader(
                new FileReader(path))) {
            int count = 0;
            while (reader.readLine() != null) {
                count++;
            }
            return count;
        }
    }
}
```

### 8.3 递归遍历目录

```java
public class DirectoryWalker {
    public static void walk(File dir, int depth) {
        if (dir.isDirectory()) {
            File[] children = dir.listFiles();
            if (children != null) {
                for (File child : children) {
                    String indent = "  ".repeat(depth);
                    if (child.isDirectory()) {
                        System.out.println(indent + "📁 " + child.getName() + "/");
                        walk(child, depth + 1);
                    } else {
                        System.out.println(indent + "📄 " + child.getName());
                    }
                }
            }
        }
    }

    public static void main(String[] args) {
        File dir = new File(args.length > 0 ? args[0] : ".");
        walk(dir, 0);
    }
}
```

---

## 9. 最佳实践与注意事项

### 9.1 资源管理

- **始终使用 try-with-resources**，确保资源自动关闭
- 多个资源在同一 try 语句中声明，用分号分隔
- 自定义资源类实现 `AutoCloseable` 接口

### 9.2 性能优化

- 使用**缓冲流**（`BufferedInputStream`/`BufferedOutputStream`）提高IO效率
- 缓冲区大小一般为 `8192`（8KB），可根据场景调整
- 字符操作优先使用 `Reader`/`Writer`，避免手动编码转换

### 9.3 编码处理

- **显式指定字符编码**，避免使用系统默认编码
- 推荐使用 `StandardCharsets.UTF_8` 常量
- `InputStreamReader`/`OutputStreamWriter` 实现字节流到字符流的转换

```java
// 正确：显式指定编码
new FileWriter("file.txt", StandardCharsets.UTF_8)
new InputStreamReader(inputStream, StandardCharsets.UTF_8)

// 不推荐：使用默认编码
new FileWriter("file.txt")  // 依赖系统默认编码
```

### 9.4 异常处理

- IO操作必须处理 `IOException`
- 区分"文件不存在"、"权限不足"、"磁盘已满"等错误
- 使用 `Files` 类的 `exists()`、`isReadable()` 等方法预检查

### 9.5 NIO.2 新API（Java 7+）

```java
// 读取整个文件
String content = Files.readString(Path.of("file.txt"));

// 写入文件
Files.writeString(Path.of("output.txt"), "Hello World");

// 文件复制
Files.copy(Path.of("source.txt"), Path.of("target.txt"),
           StandardCopyOption.REPLACE_EXISTING);

// 读取所有行
List<String> lines = Files.readAllLines(Path.of("file.txt"));

// 创建临时文件
Path tempFile = Files.createTempFile("prefix-", ".txt");
```

---

## 10. 核心知识点总结

### 10.1 流的层次结构

```
InputStream (抽象)          OutputStream (抽象)
├── FileInputStream         ├── FileOutputStream
├── ByteArrayInputStream    ├── ByteArrayOutputStream
├── BufferedInputStream     ├── BufferedOutputStream
├── DataInputStream         ├── DataOutputStream
└── ObjectInputStream       └── ObjectOutputStream

Reader (抽象)               Writer (抽象)
├── FileReader              ├── FileWriter
├── BufferedReader          ├── BufferedWriter
├── InputStreamReader       ├── OutputStreamWriter
└── StringReader            └── StringWriter
```

### 10.2 关键对比

| 特性 | 字节流 | 字符流 |
|------|--------|--------|
| 数据单位 | byte | char |
| 适用场景 | 二进制数据 | 文本数据 |
| 编码处理 | 手动处理 | 自动处理 |
| 基类 | InputStream/OutputStream | Reader/Writer |
| 缓冲类 | BufferedInputStream/OutputStream | BufferedReader/Writer |

### 10.3 记忆口诀

- **流分字节和字符**：`InputStream/OutputStream` 处理字节，`Reader/Writer` 处理字符
- **资源自动管**：使用 `try-with-resources` 自动关闭
- **缓冲提效率**：大数据量读写用缓冲流
- **编码要指定**：始终显式指定字符编码
- **flush别忘记**：需要立即输出时手动调用 `flush()`

---

## 附录：常用类速查表

| 类名 | 包路径 | 用途 |
|------|--------|------|
| `InputStream` | `java.io` | 字节输入流基类 |
| `OutputStream` | `java.io` | 字节输出流基类 |
| `Reader` | `java.io` | 字符输入流基类 |
| `Writer` | `java.io` | 字符输出流基类 |
| `FileInputStream` | `java.io` | 文件字节输入流 |
| `FileOutputStream` | `java.io` | 文件字节输出流 |
| `FileReader` | `java.io` | 文件字符输入流 |
| `FileWriter` | `java.io` | 文件字符输出流 |
| `BufferedReader` | `java.io` | 缓冲字符输入流 |
| `BufferedWriter` | `java.io` | 缓冲字符输出流 |
| `PrintWriter` | `java.io` | 格式化输出 |
| `DataInputStream` | `java.io` | 读取基本类型数据 |
| `DataOutputStream` | `java.io` | 写入基本类型数据 |
| `ObjectInputStream` | `java.io` | 反序列化对象 |
| `ObjectOutputStream` | `java.io` | 序列化对象 |
| `File` | `java.io` | 文件/目录操作 |
| `Path` | `java.nio.file` | 文件路径表示 |
| `Files` | `java.nio.file` | 文件工具类（NIO.2） |