# Node.js P6 工程师系统学习计划

> 目标：达到互联网大厂 P6 级工程师水平  
> 周期：约 6-8 个月（根据个人基础调整）  
> 评估方式：每个阶段完成自测 + 实战项目 + 面试题验证

---

## 📊 学习路线总览

```
第一阶段：夯实基础（1-2个月）
    ↓
第二阶段：企业级框架精通（2-3个月）
    ↓
第三阶段：架构设计能力（1-2个月）
    ↓
第四阶段：性能调优与高可用（1个月）
    ↓
面试冲刺准备
```

---

## 第一阶段：底层原理深度掌握

### 阶段目标
- 深入理解 Node.js 事件循环机制，能够分析复杂异步代码
- 掌握 V8 内存管理机制，能够定位和解决内存问题
- 精通 Stream 和 Buffer，能够处理大规模数据流
- 理解异步 I/O 底层实现，选择最优异步编程模式

### 1.1 Event Loop 深入理解

#### 核心知识点
- Node.js 事件循环的 6 个阶段：timers → pending callbacks → idle/prepare → poll → check → close callbacks
- setTimeout vs setImmediate 执行顺序
- process.nextTick() 和 Promise.then() 微任务执行时机
- 宏任务与微任务的执行规则

#### 学习资源

| 资源类型 | 名称 | 地址 |
|---------|------|------|
| 官方文档 | Node.js Event Loop 官方指南 | https://nodejs.org/zh-cn/docs/guides/event-loop-timers-and-nexttick |
| 官方文档 | The Node.js Event Loop | https://nodejs.org/en/docs/guides/dont-block-the-event-loop |
| 经典文章 | 深入理解 Node.js 事件循环 | https://nodejs.org/uk/docs/guides/ |
| 视频课程 | Node.js Event Loop 深度解析 | https://www.youtube.com/watch?v=PNa9OMajw9w |
| 经典文章 | JavaScript Event Loop Explained | https://blog.risingstack.com/ |

#### 实践案例
```javascript
// 案例1：分析执行顺序
console.log('1');

setTimeout(() => console.log('2'), 0);

setImmediate(() => console.log('3'));

Promise.resolve().then(() => console.log('4'));

process.nextTick(() => console.log('5'));

console.log('6');

// 思考：输出顺序是什么？为什么？
```

```javascript
// 案例2：分析 this 指向
const http = require('http');

http.createServer((req, res) => {
  // 分析异步回调中的 this 指向
  setTimeout(() => {
    console.log('setTimeout this:', this); // ？
  }, 0);
  
  setImmediate(() => {
    console.log('setImmediate this:', this); // ？
  });
  
  process.nextTick(() => {
    console.log('nextTick this:', this); // ？
  });
  
  res.end('ok');
}).listen(3000);
```

#### 自测题目
1. 解释 Node.js 事件循环的完整执行流程
2. setTimeout(fn, 0) 和 setImmediate(fn) 的区别是什么？
3. process.nextTick() 和 Promise.then() 的执行优先级？
4. 什么是 "饥饿" 问题？如何解决？

---

### 1.2 V8 内存管理与垃圾回收

#### 核心知识点
- V8 内存结构：新生代（New Space）与老生代（Old Space）
- 垃圾回收算法：Scavenge、Mark-Sweep、Mark-Compact
- 内存泄漏常见场景：全局变量、闭包、定时器、事件监听器
- 内存限制与突破方案：buffer Allocation

#### 学习资源

| 资源类型 | 名称 | 地址 |
|---------|------|------|
| 官方文档 | V8 内存管理 | https://nodejs.org/zh-cn/docs/guides/diagnostics/memory |
| 官方文档 | V8 官方博客 | https://v8.dev/blog |
| 经典文章 | 深入理解 V8 垃圾回收 | https://www.iteye.com/blogs/subjects/v8-garbage-collection |
| 工具文档 | heapdump 使用指南 | https://www.npmjs.com/package/heapdump |
| 工具文档 | clinic.js 官方文档 | https://clinicjs.org/documentation/ |
| 视频课程 | Node.js 内存泄漏排查 | https://www.youtube.com/watch?v=2ujop标准化 |

#### 实践案例
```javascript
// 案例1：内存泄漏场景 - 未清理的定时器
class MemoryLeaker {
  constructor() {
    this.data = [];
    // 内存泄漏：每秒钟累积大量数据
    this.interval = setInterval(() => {
      this.data.push(new Array(10000).fill('泄漏'));
    }, 1000);
  }
  
  // 正确清理方式
  destroy() {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
    this.data = null;
  }
}

// 案例2：使用 heapdump 排查内存
const heapdump = require('heapdump');

process.on('SIGUSR2', () => {
  heapdump.writeSnapshot((err, filename) => {
    console.log('Heap snapshot written to', filename);
  });
});
```

```javascript
// 案例3：使用 clinic.js 进行诊断
// 1. 安装：npm install -g clinic
// 2. 运行：clinic doctor -- node server.js
// 3. 分析生成的火焰图
```

#### 自测题目
1. 解释 V8 新生代和老生代的区别
2. Scavenge 算法的优缺点？
3. 什么情况下会触发 Full GC？
4. 如何定位 Node.js 应用的内存泄漏？

---

### 1.3 Stream 流与 Buffer 原理

#### 核心知识点
- Stream 的四种类型：Readable、Writable、Duplex、Transform
- 背压机制（backpressure）原理与处理
- pipe 方法实现原理
- Buffer 内存分配策略与编码转换

#### 学习资源

| 资源类型 | 名称 | 地址 |
|---------|------|------|
| 官方文档 | Stream 官方文档 | https://nodejs.org/zh-cn/docs/guides/backpressure |
| 官方文档 | Buffer 官方文档 | https://nodejs.org/zh-cn/docs/api/buffer |
| 经典文章 | Stream 实战：构建可读流 | https://nodejs.org/en/docs/guides/ |
| GitHub 仓库 | stream-handbook | https://github.com/substack/stream-handbook |
| 视频课程 | Node.js Streams 完整指南 | https://www.youtube.com/watch?v=G9VQE31 |

#### 实践案例
```javascript
// 案例1：实现背压机制
const { Readable, Writable } = require('stream');

class SlowConsumer extends Writable {
  constructor(options) {
    super(options);
    this.delay = options.delay || 100;
  }
  
  _write(chunk, encoding, callback) {
    setTimeout(() => {
      console.log('Processing:', chunk.toString());
      callback(); // 必须调用 callback 才能继续
    }, this.delay);
  }
}

class FastProducer extends Readable {
  constructor(options) {
    super(options);
    this.count = 0;
    this.max = 100;
  }
  
  _read() {
    if (this.count >= this.max) {
      this.push(null); // 结束流
    } else {
      this.count++;
      this.push(`Data ${this.count}`); // 自动触发背压
    }
  }
}

// 使用 pipe 自动处理背压
const producer = new FastProducer();
const consumer = new SlowConsumer({ delay: 10 });
producer.pipe(consumer);

// 案例2：Transform 流实现数据转换
const { Transform } = require('stream');

class UpperCaseTransform extends Transform {
  _transform(chunk, encoding, callback) {
    this.push(chunk.toString().toUpperCase());
    callback();
  }
}

const transform = new UpperCaseTransform();
process.stdin.pipe(transform).pipe(process.stdout);

// 案例3：处理大文件 - 文件复制
const fs = require('fs');
const path = require('path');

function copyFile(src, dest) {
  return new Promise((resolve, reject) => {
    const readStream = fs.createReadStream(src);
    const writeStream = fs.createWriteStream(dest);
    
    readStream.on('error', reject);
    writeStream.on('error', reject);
    writeStream.on('finish', resolve);
    
    // 使用 pipe，自动处理背压
    readStream.pipe(writeStream);
  });
}
```

#### 自测题目
1. 解释 Stream 的四种类型及应用场景
2. 什么是背压？如何处理？
3. pipe 方法的实现原理是什么？
4. Buffer 和 String 的转换有哪些编码方式？

---

### 1.4 异步 I/O 底层实现

#### 核心知识点
- libuv 线程池模型与工作原理
- 非阻塞 I/O vs 同步 I/O
- 文件系统 I/O 与网络 I/O 的实现差异
- 回调、Promise、async-await 的底层差异

#### 学习资源

| 资源类型 | 名称 | 地址 |
|---------|------|------|
| 官方文档 | libuv 官方文档 | http://docs.libuv.org/en/v1.x/ |
| 经典文章 | Understanding Node.js Async I/O | https:///blog.risingstack.com/node-js-at-scale-understanding |
| GitHub | libuv 源码分析 | https://github.com/libuv/libuv |
| 视频课程 | Node.js 异步I/O机制 | https://www.youtube.com/watch?v= |

#### 实践案例
```javascript
// 案例1：对比同步、回调、Promise、async-await
const fs = require('fs');
const path = require('path');

// 同步方式
function syncRead() {
  const data = fs.readFileSync(path.join(__dirname, 'test.txt'), 'utf8');
  console.log('Sync:', data);
  return data;
}

// 回调方式
function callbackRead(callback) {
  fs.readFile(path.join(__dirname, 'test.txt'), 'utf8', (err, data) => {
    if (err) callback(err);
    callback(null, data);
  });
}

// Promise 方式
function promiseRead() {
  return new Promise((resolve, reject) => {
    fs.readFile(path.join(__dirname, 'test.txt'), 'utf8', (err, data) => {
      if (err) reject(err);
      resolve(data);
    });
  });
}

// async/await 方式
async function asyncAwaitRead() {
  const data = await promiseRead();
  console.log('Async:', data);
  return data;
}

// 案例2：模拟 libuv 线程池
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');

if (isMainThread) {
  // 主线程调度任务
  const worker = new Worker(__filename, {
    workerData: { task: 'compute', input: 1000000000 }
  });
  
  worker.on('message', (result) => {
    console.log('Worker result:', result);
  });
} else {
  // Worker 线程执行
  const { task, input } = workerData;
  if (task === 'compute') {
    // 模拟 CPU 密集型计算
    let result = 0;
    for (let i = 0; i < input; i++) {
      result += Math.sqrt(i);
    }
    parentPort.postMessage(result);
  }
}
```

#### 自测题目
1. libuv 线程池默认大小是多少？如何修改？
2. Node.js 如何实现非阻塞 I/O？
3. Promise 和 async/await 的执行机制有什么区别？
4. 什么是 "回调地狱"？如何避免？

---

## 第二阶段：企业级框架与工程化实践

### 阶段目标
- 精通 NestJS 框架，能够构建企业级后端应用
- 掌握 IoC、DI、AOP 等核心设计模式
- 熟练使用 TypeScript、RxJS 等高级特性
- 具备完整的工程化能力：测试、CI/CD、容器化部署

### 2.1 NestJS 深度精通

#### 核心知识点
- NestJS 模块化架构与依赖注入
- 控制器、服务、模块的组织方式
- 借鉴 Java Spring 的核心思想
- 中间件、拦截器、守卫、管道、异常过滤器

#### 学习资源

| 资源类型 | 名称 | 地址 |
|---------|------|------|
| 官方文档 | NestJS 官方文档 | https://docs.nestjs.com/ |
| 官方文档 | NestJS 中文文档 | https://nestjs.com.cn/ |
| GitHub 仓库 | NestJS 源码 | https://github.com/nestjs/nest |
| 在线课程 | NestJS 实战 | https://www.youtube.com/watch?v= |
| 开源项目 | NestJS 优秀实践 | https://github.com/johnnybe/nestjs-clean-architecture |

#### 实践案例
```typescript
// 案例1：NestJS 模块化架构
// src/modules/users/users.module.ts
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { UsersController } from './users.controller';
import { UsersService } from './users.service';
import { User } from './entities/user.entity';

@Module({
  imports: [TypeOrmModule.forFeature([User])],
  controllers: [UsersController],
  providers: [UsersService],
  exports: [UsersService],
})
export class UsersModule {}

// src/modules/users/users.service.ts
import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './entities/user.entity';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,
  ) {}
  
  async findById(id: string): Promise<User> {
    const user = await this.userRepository.findOne({ where: { id } });
    if (!user) {
      throw new NotFoundException(`User with ID ${id} not found`);
    }
    return user;
  }
}

// src/modules/users/users.controller.ts
import { Controller, Get, Param, UseGuards } from '@nestjs/common';
import { UsersService } from './users.service';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}
  
  @Get(':id')
  @UseGuards(JwtAuthGuard)
  async findOne(@Param('id') id: string) {
    return this.usersService.findById(id);
  }
}
```

```typescript
// 案例2：自定义守卫实现权限控制
// src/common/guards/roles.guard.ts
import { Injectable, CanActivate, ExecutionContext } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { Role } from '../decorators/roles.decorator';

@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private reflector: Reflector) {}
  
  canActivate(context: ExecutionContext): boolean {
    const requiredRoles = this.reflector.getAllAndOverride<Role[]>('roles', [
      context.getHandler(),
      context.getClass(),
    ]);
    
    if (!requiredRoles) {
      return true;
    }
    
    const { user } = context.switchToHttp().getRequest();
    return requiredRoles.some((role) => user.roles?.includes(role));
  }
}

// src/common/decorators/roles.decorator.ts
import { SetMetadata } from '@nestjs/common';

export const Roles = (...roles: Role[]) => SetMetadata('roles', roles);
```

```typescript
// 案例3：拦截器实现统一响应格式
// src/common/interceptors/transform.interceptor.ts
import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

export interface Response<T> {
  code: number;
  data: T;
  message: string;
  timestamp: number;
}

@Injectable()
export class TransformInterceptor<T>
  implements NestInterceptor<T, Response<T>>
{
  intercept(
    context: ExecutionContext,
    next: CallHandler,
  ): Observable<Response<T>> {
    return next.handle().pipe(
      map((data) => ({
        code: 0,
        data,
        message: 'success',
        timestamp: Date.now(),
      })),
    );
  }
}
```

#### 自测题目
1. NestJS 的模块化设计原则是什么？
2. 解释依赖注入在 NestJS 中的应用
3. 守卫、拦截器、管道、过滤器的区别和使用场景？
4. NestJS 如何实现 AOP 编程？

---

### 2.2 核心设计模式与思想

#### 2.2.1 IoC 与 DI（控制反转与依赖注入）

#### 学习资源

| 资源类型 | 名称 | 地址 |
|---------|------|------|
| 官方文档 | NestJS 依赖注入 | https://docs.nestjs.com/fundamentals/dependency-injection |
| 经典文章 | IoC vs DI 详解 | https://www.cnblogs.com/ |

#### 实践案例
```typescript
// 案例1：NestJS 依赖注入的三种方式
import { Injectable, Inject, Optional, Self } from '@nestjs/common';

// 标准构造函数注入
@Injectable()
class UserService {
  constructor(private readonly userRepository: UserRepository) {}
}

// 属性注入（不推荐，影响测试性）
@Injectable()
class UserController {
  @Inject('USER_REPOSITORY')
  private readonly userRepository: UserRepository;
}

// 可选注入
@Injectable()
class ConfigService {
  constructor(
    @Optional() @Inject('CONFIG') private readonly config: Config,
  ) {
    this.config = config || { port: 3000 };
  }
}

// 自定义 Provider
@Module({
  providers: [
    {
      provide: 'USER_SERVICE',
      useClass: UserService,
    },
    {
      provide: 'CONFIG',
      useFactory: () => process.env,
    },
    {
      provide: 'ASYNC_SERVICE',
      useFactory: async () => {
        const data = await fetchData();
        return new AsyncService(data);
      },
      inject: [ExternalService],
    },
  ],
})
export class AppModule {}
```

#### 2.2.2 AOP（面向切面编程）

#### 实践案例
```typescript
// 案例2：AOP 实现性能日志
// src/common/decorators/log.decorator.ts
import { Logger } from '@nestjs/common';

export function Log(message: string) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor,
  ) {
    const original = descriptor.value;
    
    descriptor.value = async function (...args: any[]) {
      const logger = new Logger(target.constructor.name);
      const start = Date.now();
      
      logger.log(`${message} - 开始`);
      
      try {
        const result = await original.apply(this, args);
        const duration = Date.now() - start;
        logger.log(`${message} - 完成，耗时: ${duration}ms`);
        return result;
      } catch (error) {
        const duration = Date.now() - start;
        logger.error(`${message} - 失败，耗时: ${duration}ms`, error.stack);
        throw error;
      }
    };
    
    return descriptor;
  };
}

// 使用
class UserService {
  @Log('获取用户列表')
  async findAll() {
    // ...
  }
}
```

#### 2.2.3 装饰器模式

#### 实践案例
```typescript
// 案例3：自定义装饰器实现权限验证
import { createParamDecorator, ExecutionContext } from '@nestjs/common';

// 获取当前用户
export const CurrentUser = createParamDecorator(
  (data: string, ctx: ExecutionContext) => {
    const request = ctx.switchToHttp().getRequest();
    const user = request.user;
    
    return data ? user?.[data] : user;
  },
);

// 使用
@Controller('users')
class UserController {
  @Get('profile')
  getProfile(@CurrentUser() user: User) {
    return user;
  }
  
  @Get('profile/:field')
  getProfileField(
    @CurrentUser('id') userId: string,
  ) {
    return { userId };
  }
}
```

#### 2.2.4 RxJS 响应式编程

#### 学习资源

| 资源类型 | 名称 | 地址 |
|---------|------|------|
| 官方文档 | RxJS 官方文档 | https://rxjs.dev/guide/overview |
| 中文文档 | RxJS 中文网 | https://cn.rx.js.org/ |
| GitHub 仓库 | RxJS 源码 | https://github.com/ReactiveX/rxjs |

#### 实践案例
```typescript
// 案例4：RxJS 实战 - 搜索建议
import { fromEvent, Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap, takeUntil } from 'rxjs/operators';

@Injectable()
export class SearchService {
  private destroy$ = new Subject<void>();
  
  setupSearch(input: HTMLInputElement) {
    fromEvent(input, 'input').pipe(
      debounceTime(300), // 300ms 防抖
      distinctUntilChanged(), // 过滤重复值
      switchMap((event) => this.fetchSuggestions(event.target.value)), // 切换到最新请求
      takeUntil(this.destroy$), // 组件销毁时取消订阅
    ).subscribe((suggestions) => {
      this.updateSuggestions(suggestions);
    });
  }
  
  private fetchSuggestions(query: string): Observable<string[]> {
    return this.http.get<string[]>(`/api/suggestions?q=${query}`);
  }
  
  destroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

```typescript
// 案例5：RxJS 操作符组合使用
import { of, interval } from 'rxjs';
import { map, filter, reduce, catchError, retry, share } from 'rxjs/operators';

const numbers$ = of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

numbers$.pipe(
  filter(n => n % 2 === 0), // 过滤偶数
  map(n => n * n), // 平方
  reduce((acc, val) => acc + val, 0), // 求和
).subscribe(result => console.log('Result:', result)); // 输出: 2^2 + 4^2 + 6^2 + 8^2 + 10^2 = 220

// 带错误处理的请求
const data$ = this.http.get('/api/data').pipe(
  retry(3), // 重试3次
  catchError(error => {
    console.error('请求失败:', error);
    return of(null);
  }),
  share(), // 共享 Observable
);
```

#### 自测题目
1. IoC 和 DI 的区别是什么？
2. NestJS 中如何实现自定义 Provider？
3. AOP 的核心概念和应用场景？
4. RxJS 中 map、filter、switchMap、concatMap 的区别？

---

### 2.3 工程化实践

#### 2.3.1 TypeScript 高级特性

#### 学习资源

| 资源类型 | 名称 | 地址 |
|---------|------|------|
| 官方文档 | TypeScript 官方文档 | https://www.typescriptlang.org/docs/ |
| 中文文档 | TypeScript 中文文档 | https://www.tslang.cn/docs/home.html |
| 书籍 | 《Programming TypeScript》 | https://www.oreilly.com/library/view/programming-typescript/ |

#### 实践案例
```typescript
// 案例1：TypeScript 高级类型
// 泛型约束
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

// 条件类型
type NonNullable<T> = T extends null | undefined ? never : T;

// 映射类型
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

type Partial<T> = {
  [P in keyof T]?: T[P];
};

type Pick<T, K extends keyof T> = {
  [P in K]: T[P];
};

type Record<K extends string, T> = {
  [P in K]: T;
};

// 装饰器类型
function log(target: any, key: string, descriptor: PropertyDescriptor) {
  const original = descriptor.value;
  descriptor.value = function (...args: any[]) {
    console.log(`Calling ${key} with`, args);
    return original.apply(this, args);
  };
  return descriptor;
}

// 泛型类
class DataStore<T> {
  private items: T[] = [];
  
  add(item: T): this {
    this.items.push(item);
    return this;
  }
  
  get(index: number): T | undefined {
    return this.items[index];
  }
  
  map<U>(fn: (item: T) => U): U[] {
    return this.items.map(fn);
  }
}

// 接口继承
interface Person {
  name: string;
  age: number;
}

interface Employee extends Person {
  employeeId: string;
  department: string;
}

// 类型守卫
function isString(value: unknown): value is string {
  return typeof value === 'string';
}
```

```typescript
// 案例2：模块系统与命名空间
// types/user.ts
export interface User {
  id: string;
  name: string;
  email: string;
}

// types/index.ts
export * from './user';

// utils/validation.ts
export function validateEmail(email: string): boolean {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}
```

#### 2.3.2 代码规范（ESLint + Prettier）

#### 学习资源

| 资源类型 | 名称 | 地址 |
|---------|------|------|
| 官方文档 | ESLint 官方文档 | https://eslint.org/docs/user-guide/getting-started |
| 官方文档 | Prettier 官方文档 | https://prettier.io/docs/en/index.html |
| 配置集合 | eslint-config-airbnb | https://github.com/airbnb/javascript |

#### 实践案例
```javascript
// .eslintrc.js
module.exports = {
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 2021,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
  },
  extends: [
    'airbnb-base',
    'plugin:@typescript-eslint/recommended',
    'plugin:prettier/recommended',
  ],
  plugins: ['@typescript-eslint', 'prettier'],
  rules: {
    'prettier/prettier': 'error',
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
  },
};

// .prettierrc
{
  "semi": true,
  "trailingComma": "all",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "arrowParens": "always"
}
```

#### 2.3.3 测试实践（Jest + Supertest）

#### 学习资源

| 资源类型 | 名称 | 地址 |
|---------|------|------|
| 官方文档 | Jest 官方文档 | https://jestjs.io/docs/getting-started |
| 官方文档 | Supertest 官方文档 | https://github.com/visionmedia/supertest |
| 官方文档 | NestJS 测试 | https://docs.nestjs.com/fundamentals/testing |

#### 实践案例
```typescript
// users.service.spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { getRepositoryToken } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { UsersService } from './users.service';
import { User } from './entities/user.entity';

describe('UsersService', () => {
  let service: UsersService;
  let repository: Repository<User>;
  
  const mockUser: User = {
    id: '1',
    name: 'Test User',
    email: 'test@example.com',
    password: 'hashedPassword',
    createdAt: new Date(),
    updatedAt: new Date(),
  };
  
  const mockRepository = {
    find: jest.fn(),
    findOne: jest.fn(),
    create: jest.fn(),
    save: jest.fn(),
    delete: jest.fn(),
  };
  
  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        UsersService,
        {
          provide: getRepositoryToken(User),
          useValue: mockRepository,
        },
      ],
    }).compile();
    
    service = module.get<UsersService>(UsersService);
    repository = module.get<Repository<User>>(getRepositoryToken(User));
  });
  
  it('should be defined', () => {
    expect(service).toBeDefined();
  });
  
  describe('findAll', () => {
    it('should return an array of users', async () => {
      const expectedUsers = [mockUser];
      mockRepository.find.mockResolvedValue(expectedUsers);
      
      const result = await service.findAll();
      
      expect(result).toEqual(expectedUsers);
      expect(mockRepository.find).toHaveBeenCalled();
    });
  });
  
  describe('findById', () => {
    it('should return a user by id', async () => {
      mockRepository.findOne.mockResolvedValue(mockUser);
      
      const result = await service.findById('1');
      
      expect(result).toEqual(mockUser);
    });
    
    it('should throw NotFoundException if user not found', async () => {
      mockRepository.findOne.mockResolvedValue(null);
      
      await expect(service.findById('999')).rejects.toThrow(NotFoundException);
    });
  });
});
```

```typescript
// users.controller.e2e-spec.ts
import { Test } from '@nestjs/testing';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';

describe('UsersController (e2e)', () => {
  let app: INestApplication;
  
  beforeAll(async () => {
    const moduleFixture = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();
    
    app = moduleFixture.createNestApplication();
    await app.init();
  });
  
  afterAll(async () => {
    await app.close();
  });
  
  describe('/GET users', () => {
    it('should return an array of users', () => {
      return request(app.getHttpServer())
        .get('/users')
        .set('Authorization', `Bearer ${global.token}`)
        .expect(200)
        .expect((res) => {
          expect(Array.isArray(res.body.data)).toBe(true);
        });
    });
  });
});
```

#### 2.3.4 CI/CD 与容器化

#### 学习资源

| 资源类型 | 名称 | 地址 |
|---------|------|------|
| 官方文档 | GitHub Actions | https://docs.github.com/en/actions |
| 官方文档 | Docker 官方文档 | https://docs.docker.com/ |
| 官方文档 | GitLab CI | https://docs.gitlab.com/ee/ci/ |

#### 实践案例
```yaml
# .github/workflows/nodejs.yml
name: Node.js CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Run linter
        run: npm run lint
        
      - name: Run tests
        run: npm run test:cov
        
      - name: Build
        run: npm run build
        
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: dist
          path: dist/
```

```dockerfile
# Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM node:18-alpine AS runner

WORKDIR /app

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./

ENV NODE_ENV=production

USER node

EXPOSE 3000

CMD ["node", "dist/main.js"]
```

---

## 第三阶段：架构设计能力培养

### 阶段目标
- 掌握 BFF 架构设计，能够优化前后端数据交互
- 理解微服务架构，具备服务拆分与治理能力
- 掌握网关设计，实现鉴权、限流、熔断等能力
- 能够设计高可用、可扩展的系统架构

### 3.1 BFF（Backend For Frontend）架构

#### 学习资源

| 资源类型 | 名称 | 地址 |
|---------|------|------|
| 经典文章 | BFF 架构详解 | https://www.thoughtworks.com/ |
| 开源项目 | BFF 示例项目 | https://github.com/ |

#### 实践案例
```typescript
// 案例1：BFF 层实现接口聚合
// src/bff/user-bff.service.ts
@Injectable()
export class UserBffService {
  constructor(
    private readonly userService: UserService,
    private readonly orderService: OrderService,
    private readonly balanceService: BalanceService,
  ) {}
  
  async getUserDashboard(userId: string) {
    // 并行请求多个服务
    const [user, orders, balance] = await Promise.all([
      this.userService.getUserById(userId),
      this.orderService.getRecentOrders(userId, 10),
      this.balanceService.getBalance(userId),
    ]);
    
    return {
      user: {
        id: user.id,
        name: user.name,
        avatar: user.avatar,
        level: user.level,
      },
      recentOrders: orders.map(order => ({
        id: order.id,
        status: order.status,
        total: order.totalAmount,
        createdAt: order.createdAt,
      })),
      balance: balance.available,
      stats: {
        totalOrders: orders.length,
        memberDays: this.calculateMemberDays(user.createdAt),
      },
    };
  }
}

// 案例2：Next.js SSR 实现
// pages/user/[id].tsx
export async function getServerSideProps(context: GetServerSidePropsContext) {
  const { id } = context.params;
  
  const user = await userService.getUserById(id);
  
  if (!user) {
    return { notFound: true };
  }
  
  return {
    props: {
      user: JSON.parse(JSON.stringify(user)),
    },
  };
}

function UserPage({ user }: { user: User }) {
  return (
    <div>
      <h1>{user.name}</h1>
      <UserProfile user={user} />
    </div>
  );
}
```

#### 自测题目
1. BFF 的核心作用是什么？
2. 什么时候应该使用 SSR vs CSR？
3. 如何处理 BFF 层的错误和降级？

---

### 3.2 微服务架构

#### 学习资源

| 资源类型 | 名称 | 地址 |
|---------|------|------|
| 官方文档 | gRPC 官方文档 | https://grpc.io/docs/ |
| 官方文档 | Kafka 官方文档 | https://kafka.apache.org/documentation/ |
| 官方文档 | RabbitMQ 官方文档 | https://www.rabbitmq.com/documentation.html |
| 开源项目 | NestJS Microservices | https://docs.nestjs.com/microservices/basics |

#### 实践案例
```typescript
// 案例1：gRPC 服务定义
// proto/user.proto
syntax = "proto3";

package user;

service UserService {
  rpc GetUser (GetUserRequest) returns (User);
  rpc ListUsers (ListUsersRequest) returns (ListUsersResponse);
  rpc CreateUser (CreateUserRequest) returns (User);
}

message GetUserRequest {
  string id = 1;
}

message User {
  string id = 1;
  string name = 2;
  string email = 3;
}

message ListUsersRequest {
  int32 page = 1;
  int32 pageSize = 2;
}

message ListUsersResponse {
  repeated User users = 1;
  int32 total = 2;
}

// NestJS gRPC 服务实现
// user.service.ts
@GrpcMethod('UserService', 'GetUser')
getUser(request: GetUserRequest): User {
  return this.userService.findById(request.id);
}

// 案例2：Kafka 消息队列
// producer.service.ts
@Injectable()
export class UserEventProducer {
  constructor(@Inject('KAFKA_PRODUCER') private producer: KafkaProducer) {}
  
  async publishUserCreated(user: User) {
    await this.producer.send({
      topic: 'user-events',
      messages: [
        {
          key: user.id,
          value: JSON.stringify({
            event: 'USER_CREATED',
            data: user,
            timestamp: Date.now(),
          }),
        },
      ],
    });
  }
}

// consumer.service.ts
@Injectable()
export class UserEventConsumer {
  @KafkaSubscribe('user-events', {
    groupId: 'notification-service',
  })
  async handleUserCreated(message: ConsumeMessage) {
    const { event, data } = JSON.parse(message.value.toString());
    
    if (event === 'USER_CREATED') {
      await this.notificationService.sendWelcomeEmail(data.email);
    }
  }
}
```

```typescript
// 案例3：服务注册与发现
// src/app.module.ts
import { ConsulModule } from 'nestjs-consul';

@Module({
  imports: [
    ConsulModule.register({
      host: 'localhost',
      port: 8500,
    }),
  ],
})
export class AppModule {}

// src/users/users.service.ts
@Injectable()
export class UsersService {
  constructor(
    @Inject('CONSUL_SERVICE')
    private readonly consul: ConsulService,
  ) {}
  
  async findService(serviceName: string) {
    const instances = await this.consul.serviceInstances(serviceName);
    return this.loadBalance.select(instances);
  }
}
```

#### 自测题目
1. gRPC 和 REST 的区别是什么？各自适用场景？
2. Kafka 和 RabbitMQ 的区别？如何选型？
3. 什么是服务治理？包含哪些核心组件？

---

### 3.3 网关层设计

#### 实践案例
```typescript
// 案例1：JWT 鉴权
// src/auth/jwt.strategy.ts
@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {}

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor() {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: process.env.JWT_SECRET,
    });
  }
  
  async validate(payload: any) {
    return { userId: payload.sub, email: payload.email };
  }
}

// 案例2：限流实现
// src/common/guards/rate-limit.guard.ts
@Injectable()
export class RateLimitGuard implements CanActivate {
  constructor(private readonly rateLimiter: RateLimiter) {}
  
  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const key = request.ip;
    const limit = 100; // 100 requests per minute
    const window = 60; // 60 seconds
    
    const result = await this.rateLimiter.check(key, limit, window);
    
    if (!result.success) {
      throw new ThrottlerException('请求过于频繁');
    }
    
    return true;
  }
}

// 令牌桶算法实现
class TokenBucket {
  private tokens: number;
  private lastRefill: number;
  
  constructor(
    private capacity: number,
    private refillRate: number, // tokens per second
  ) {
    this.tokens = capacity;
    this.lastRefill = Date.now();
  }
  
  async acquire(tokens: number = 1): Promise<boolean> {
    this.refill();
    
    if (this.tokens >= tokens) {
      this.tokens -= tokens;
      return true;
    }
    
    return false;
  }
  
  private refill() {
    const now = Date.now();
    const elapsed = (now - this.lastRefill) / 1000;
    const tokensToAdd = elapsed * this.refillRate;
    
    this.tokens = Math.min(this.capacity, this.tokens + tokensToAdd);
    this.lastRefill = now;
  }
}

// 案例3：熔断器实现
class CircuitBreaker {
  private failures = 0;
  private lastFailure: number = 0;
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED';
  
  constructor(
    private readonly threshold: number = 5,
    private readonly timeout: number = 60000, // 60 seconds
  ) {}
  
  async execute<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailure >= this.timeout) {
        this.state = 'HALF_OPEN';
      } else {
        throw new Error('Circuit breaker is OPEN');
      }
    }
    
    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }
  
  private onSuccess() {
    this.failures = 0;
    this.state = 'CLOSED';
  }
  
  private onFailure() {
    this.failures++;
    this.lastFailure = Date.now();
    
    if (this.failures >= this.threshold) {
      this.state = 'OPEN';
    }
  }
}
```

#### 自测题目
1. JWT 和 OAuth2.0 的区别？
2. 令牌桶和漏桶算法的区别？
3. 什么是雪崩效应？如何避免？

---

## 第四阶段：性能调优与高可用保障

### 阶段目标
- 掌握性能问题诊断方法，能够定位 CPU 和内存问题
- 理解 Node.js 并发模型，能够设计高并发架构
- 精通数据库优化，能够处理大数据量和高并发场景

### 4.1 性能问题诊断

#### 学习资源

| 资源类型 | 名称 | 地址 |
|---------|------|------|
| 官方文档 | Node.js 诊断指南 | https://nodejs.org/zh-cn/docs/guides/diagnostics/ |
| 官方文档 | Chrome DevTools | https://developer.chrome.com/docs/devtools/ |
| 工具文档 | clinic.js | https://clinicjs.org/documentation/ |
| 工具文档 | 0x | https://github.com/davidmarkclements/0x |

#### 实践案例
```javascript
// 案例1：CPU Profiling
// 启动诊断
// node --prof server.js

// 处理请求后
// node --prof-process isolate-*.log > profile.txt

// 使用 clinic.js
// clinic doctor -- node server.js
// clinic flame -- node server.js
// clinic bubbleprof -- node server.js

// 案例2：内存泄漏排查
const heapdump = require('heapdump');

// 定期生成快照
setInterval(() => {
  heapdump.writeSnapshot((err, filename) => {
    if (err) {
      console.error('Snapshot failed:', err);
    } else {
      console.log('Snapshot written to', filename);
    }
  });
}, 60000 * 5); // 每5分钟

// 对比快照
const { snapshots } = require('heapdump');
const diff = require('heapdump-diff');

async function analyzeMemory() {
  const before = await snapshots.takeSnapshot();
  await runHeavyOperation();
  const after = await snapshots.takeSnapshot();
  
  const report = diff(before, after);
  console.log('Memory changes:', report);
}

// 案例3：使用 Async Hooks 进行追踪
const async_hooks = require('async_hooks');

const hook = async_hooks.createHook({
  init(asyncId, type, triggerAsyncId, resource) {
    console.log(`AsyncInit: ${type} (${asyncId}), trigger: ${triggerAsyncId}`);
  },
  before(asyncId) {
    console.log(`Before: ${asyncId}`);
  },
  after(asyncId) {
    console.log(`After: ${asyncId}`);
  },
  destroy(asyncId) {
    console.log(`Destroy: ${asyncId}`);
  },
});

hook.enable();
```

```javascript
// 案例4：OpenTelemetry 全链路追踪
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { JaegerExporter } = require('@opentelemetry/exporter-jaeger');

const sdk = new NodeSDK({
  traceExporter: new JaegerExporter({
    endpoint: 'http://localhost:14268/api/traces',
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();

process.on('SIGTERM', () => {
  sdk.shutdown()
    .then(() => console.log('Tracing terminated'))
    .catch((error) => console.log('Error terminating tracing', error))
    .finally(() => process.exit(0));
});
```

#### 自测题目
1. 如何定位 Node.js 应用的 CPU 热点？
2. 内存泄漏的常见原因有哪些？
3. 如何使用火焰图分析性能问题？

---

### 4.2 并发处理

#### 实践案例
```javascript
// 案例1：Cluster 模块实现负载均衡
const cluster = require('cluster');
const numCPUs = require('os').cpus().length;

if (cluster.isMaster) {
  console.log(`Master ${process.pid} is running`);
  
  // 衍生工作进程
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }
  
  cluster.on('exit', (worker, code, signal) => {
    console.log(`worker ${worker.process.pid} died`);
    // 重启 worker
    cluster.fork();
  });
} else {
  // 工作进程可以共享任何 TCP 连接
  // 在这里创建 HTTP 服务器
  const server = require('http').createServer((req, res) => {
    res.writeHead(200);
    res.end(`Hello from ${process.pid}`);
  });
  
  server.listen(3000);
  console.log(`Worker ${process.pid} started`);
}

// 案例2：Worker Threads 处理 CPU 密集任务
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');

function runWorker(workerData) {
  return new Promise((resolve, reject) => {
    const worker = new Worker(__filename, {
      workerData,
    });
    
    worker.on('message', resolve);
    worker.on('error', reject);
    worker.on('exit', (code) => {
      if (code !== 0) {
        reject(new Error(`Worker stopped with exit code ${code}`));
      }
    });
  });
}

if (!isMainThread) {
  // Worker 线程执行的任务
  const { start, end } = workerData;
  
  // 模拟 CPU 密集型计算
  let result = 0;
  for (let i = start; i <= end; i++) {
    result += Math.sqrt(i);
  }
  
  parentPort.postMessage(result);
}

// 主线程使用
async function main() {
  const chunkSize = 10000000;
  const numChunks = 10;
  const promises = [];
  
  for (let i = 0; i < numChunks; i++) {
    const start = i * chunkSize;
    const end = start + chunkSize;
    promises.push(runWorker({ start, end }));
  }
  
  const results = await Promise.all(promises);
  const total = results.reduce((sum, val) => sum + val, 0);
  console.log('Total:', total);
}
```

```javascript
// 案例3：连接池实现
class ConnectionPool {
  constructor(options) {
    this.size = options.size || 10;
    this.freeConnections = [];
    this.usedConnections = [];
    this.pendingRequests = [];
  }
  
  async acquire() {
    if (this.freeConnections.length > 0) {
      const conn = this.freeConnections.pop();
      this.usedConnections.push(conn);
      return conn;
    }
    
    if (this.usedConnections.length < this.size) {
      const conn = await this.createConnection();
      this.usedConnections.push(conn);
      return conn;
    }
    
    return new Promise((resolve) => {
      this.pendingRequests.push(resolve);
    });
  }
  
  release(conn) {
    const index = this.usedConnections.indexOf(conn);
    if (index > -1) {
      this.usedConnections.splice(index, 1);
      this.freeConnections.push(conn);
    }
    
    if (this.pendingRequests.length > 0) {
      const pendingResolve = this.pendingRequests.shift();
      pendingResolve(conn);
    }
  }
  
  async createConnection() {
    // 创建数据库连接
  }
}
```

#### 自测题目
1. Cluster 和 Worker Threads 的区别？
2. 如何设计线程池？
3. 什么是事件驱动模型的局限？

---

### 4.3 数据库优化

#### 实践案例
```sql
-- 案例1：MySQL 索引优化
-- 创建复合索引
CREATE INDEX idx_user_status_created ON orders(user_id, status, created_at);

-- 查询优化分析
EXPLAIN SELECT * FROM orders 
WHERE user_id = '123' 
AND status = 'completed' 
ORDER BY created_at DESC 
LIMIT 10;

-- 索引覆盖查询
CREATE INDEX idx_covering ON orders(user_id, status, created_at, order_id);

-- 案例2：分库分表
-- 按 user_id 哈希分片
-- 假设分 32 库 x 32 表
-- 分片键计算: (user_id % 32) -> 库, ((user_id / 32) % 32) -> 表

-- 案例3：读写分离配置
-- 主库写入
-- 从库读取（配置延迟复制）

-- NestJS TypeORM 配置
TypeOrmModule.forRoot({
  type: 'mysql',
  replication: {
    master: {
      host: 'master.db.com',
      port: 3306,
      username: 'root',
      password: 'password',
      database: 'main',
    },
    slaves: [
      { host: 'slave1.db.com', port: 3306, username: 'root', password: 'password', database: 'main' },
      { host: 'slave2.db.com', port: 3306, username: 'root', password: 'password', database: 'main' },
    ],
  },
});
```

```javascript
// 案例4：Redis 缓存策略
const redis = require('ioredis');

// 分布式锁
async function acquireLock(key, ttl = 30000) {
  const lockKey = `lock:${key}`;
  const lockValue = Date.now().toString();
  
  const result = await redis.set(lockKey, lockValue, 'PX', ttl, 'NX');
  
  if (result === 'OK') {
    return lockValue;
  }
  
  return null;
}

async function releaseLock(key, lockValue) {
  const lockKey = `lock:${key}`;
  
  // Lua 脚本保证原子性
  const script = `
    if redis.call("get", KEYS[1]) == ARGV[1] then
      return redis.call("del", KEYS[1])
    else
      return 0
    end
  `;
  
  await redis.eval(script, 1, lockKey, lockValue);
}

// 缓存防雪崩
async function cacheWithRandomTTL(key, fetchFn, baseTTL = 3600) {
  const randomTTL = baseTTL + Math.floor(Math.random() * baseTTL * 0.2);
  
  const cached = await redis.get(key);
  if (cached) {
    return JSON.parse(cached);
  }
  
  const data = await fetchFn();
  await redis.setex(key, randomTTL, JSON.stringify(data));
  
  return data;
}
```

#### 自测题目
1. MySQL 的 InnoDB 和 MyISAM 引擎区别？
2. 什么是数据库的三大范式？
3. Redis 的持久化机制有哪些？

---

## 实战项目路径

### 项目一：个人博客系统（1-2周）
- 技术栈：Express + MongoDB + EJS
- 功能：文章 CRUD、评论、标签、搜索
- 目标：掌握基础 Web 开发

### 项目二：RESTful API 服务（2-3周）
- 技术栈：NestJS + TypeORM + PostgreSQL
- 功能：完整的用户认证（JWT）、权限管理、CRUD API
- 目标：掌握企业级 API 开发

### 项目三：BFF 层与微服务（3-4周）
- 技术栈：NestJS（Gateway）+ gRPC + Kafka
- 功能：多服务通信、消息队列、接口聚合
- 目标：掌握微服务架构

### 项目四：性能优化实战（2-3周）
- 技术栈：所有学过的性能诊断工具
- 功能：全链路追踪、性能监控、熔断降级
- 目标：掌握性能调优

### 项目五：完整电商后端系统（4-6周）
- 技术栈：NestJS + MySQL + Redis + Kafka + Docker
- 功能：订单系统、支付系统、用户系统、秒杀系统
- 目标：达到 P6 水平

---

## 面试准备策略

### 核心知识点清单

#### Node.js 基础
- [ ] Event Loop 完整执行流程
- [ ] 进程与线程的区别
- [ ] Cluster 模块原理
- [ ] Buffer 与 Stream
- [ ] 内存管理与垃圾回收

#### 框架与工程化
- [ ] NestJS 核心原理
- [ ] 依赖注入实现
- [ ] TypeScript 高级类型
- [ ] 测试策略（单元/集成/E2E）

#### 架构设计
- [ ] BFF 架构设计
- [ ] 微服务通信方式
- [ ] 服务治理组件
- [ ] 网关设计

#### 数据库
- [ ] MySQL 索引原理
- [ ] Redis 持久化与集群
- [ ] 分库分表方案
- [ ] 数据库优化技巧

#### 性能优化
- [ ] CPU/内存问题诊断
- [ ] 并发模型理解
- [ ] 缓存策略
- [ ] 全链路追踪

### 常见面试题

```typescript
// 题目1：实现一个 Promise.all
function promiseAll(promises) {
  return new Promise((resolve, reject) => {
    const results = [];
    let completed = 0;
    
    promises.forEach((promise, index) => {
      Promise.resolve(promise)
        .then((value) => {
          results[index] = value;
          completed++;
          
          if (completed === promises.length) {
            resolve(results);
          }
        })
        .catch(reject);
    });
    
    if (promises.length === 0) {
      resolve([]);
    }
  });
}

// 题目2：实现防抖函数
function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;
  
  return function (...args: Parameters<T>) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      fn.apply(this, args);
    }, delay);
  };
}

// 题目3：实现节流函数
function throttle<T extends (...args: any[]) => any>(
  fn: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  
  return function (...args: Parameters<T>) {
    if (!inThrottle) {
      fn.apply(this, args);
      inThrottle = true;
      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
}

// 题目4：实现 LRU 缓存
class LRUCache<K, V> {
  private capacity: number;
  private cache: Map<K, V>;
  
  constructor(capacity: number) {
    this.capacity = capacity;
    this.cache = new Map();
  }
  
  get(key: K): V | undefined {
    if (!this.cache.has(key)) {
      return undefined;
    }
    
    const value = this.cache.get(key)!;
    this.cache.delete(key);
    this.cache.set(key, value);
    
    return value;
  }
  
  put(key: K, value: V): void {
    if (this.cache.has(key)) {
      this.cache.delete(key);
    } else if (this.cache.size >= this.capacity) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    
    this.cache.set(key, value);
  }
}

// 题目5：实现浅拷贝和深拷贝
function shallowClone<T extends object>(obj: T): T {
  return { ...obj };
}

function deepClone<T extends object>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }
  
  if (Array.isArray(obj)) {
    return obj.map(item => deepClone(item)) as any;
  }
  
  const cloned = {} as T;
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      cloned[key] = deepClone(obj[key]);
    }
  }
  
  return cloned;
}
```

---

## 学习资源汇总

### 官方文档
| 技术 | 地址 |
|------|------|
| Node.js | https://nodejs.org/zh-cn/docs/ |
| NestJS | https://docs.nestjs.com/ |
| TypeScript | https://www.typescriptlang.org/docs/ |
| RxJS | https://rxjs.dev/guide/overview |
| gRPC | https://grpc.io/docs/ |
| Kafka | https://kafka.apache.org/documentation/ |
| Redis | https://redis.io/documentation |
| MySQL | https://dev.mysql.com/doc/ |

### 经典书籍
| 书名 | 说明 |
|------|------|
| 《Node.js 深入浅出》 | Node.js 基础与核心原理 |
| 《深入理解 Node.js：核心技术与最佳实践》 | 底层机制与性能优化 |
| 《NestJS 实战》 | 企业级 Node.js 框架 |
| 《TypeScript 实战》 | TypeScript 深度应用 |
| 《高性能 MySQL》 | 数据库优化经典 |
| 《Redis 设计与实现》 | Redis 内部原理 |

### 在线课程
| 课程 | 平台 |
|------|------|
| Node.js 高级实战 | 慕课网 |
| NestJS 核心技术 | 极客时间 |
| TypeScript 进阶 | 前端进阶 |

---

## 评估标准

### P6 工程师能力模型

| 能力维度 | P5（初级） | P6（中级） | P7（高级） |
|---------|-----------|-----------|-----------|
| 技术深度 | 掌握基础用法 | 理解原理与源码 | 能够定制改造 |
| 架构能力 | 能够实现模块 | 能够设计系统 | 能够规划架构 |
| 问题解决 | 解决已知问题 | 解决复杂问题 | 预防未知问题 |
| 影响力 | 团队内部 | 跨团队协作 | 部门/公司级 |
| 业务理解 | 了解本业务 | 理解多业务 | 战略规划 |

### 自我评估检查清单

#### 阶段一完成标准
- [ ] 能够解释 Node.js 事件循环完整流程
- [ ] 能够定位和解决内存泄漏问题
- [ ] 能够实现自定义 Stream
- [ ] 能够分析异步代码执行顺序

#### 阶段二完成标准
- [ ] 能够构建完整的 NestJS 应用
- [ ] 能够实现自定义 DI 容器
- [ ] 能够编写完整的测试用例
- [ ] 能够配置 CI/CD 流程

#### 阶段三完成标准
- [ ] 能够设计 BFF 架构
- [ ] 能够实现微服务通信
- [ ] 能够设计网关鉴权与限流
- [ ] 能够实现熔断降级

#### 阶段四完成标准
- [ ] 能够使用工具定位性能问题
- [ ] 能够设计高并发架构
- [ ] 能够优化数据库性能
- [ ] 能够处理分布式事务

---

> 制定时间：2025年11月  
> 适用人群：有一定 JavaScript/Node.js 基础的开发者  
> 建议：根据个人基础调整学习节奏，重点突破薄弱环节
