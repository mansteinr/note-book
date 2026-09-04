# 微信小程序 Top 30 常见面试问题及详细答案

> 适合：微信小程序开发、前端开发、移动端开发岗位面试复习。  
> 重点覆盖：双线程架构、生命周期、setData、组件通信、登录鉴权、网络请求、分包、性能优化、Canvas、支付等。

---

## 1. 微信小程序的架构原理是什么？

微信小程序核心采用**逻辑层与渲染层分离**的架构。

```text
                微信小程序
                    │
         ┌──────────┴──────────┐
         │                     │
       逻辑层                渲染层
     JavaScript           WXML / WXSS
         │                     │
         └─────── Native ──────┘
                    │
             微信原生能力
```

### 逻辑层

主要负责：

- JavaScript 业务逻辑
- 生命周期
- 数据处理
- 网络请求
- API 调用
- 状态管理

### 渲染层

主要负责：

- WXML
- WXSS
- 页面渲染
- 用户交互

### Native 层

负责：

- 网络
- 文件
- 相机
- 定位
- 蓝牙
- 支付等微信原生能力

### 面试回答

> 微信小程序采用逻辑层和渲染层分离的架构。逻辑层负责 JavaScript 业务逻辑和数据处理，渲染层负责 WXML 和 WXSS 的页面展示，两者通过 Native 层进行通信。这种设计可以提高安全性和稳定性，但也带来了跨层通信成本，所以需要重点优化 setData 和渲染性能。

---

## 2. 为什么微信小程序采用双线程架构？

主要原因有三个。

### ① 安全性

如果 JavaScript 直接运行在 WebView 中，就可能直接操作浏览器环境。

小程序希望限制 JavaScript 对底层环境的直接访问，因此将逻辑和渲染隔离。

### ② 稳定性

业务 JavaScript 与页面渲染相互隔离，可以降低业务逻辑直接影响渲染环境的风险。

### ③ 架构设计

通过逻辑层、渲染层和 Native 层进行职责划分，方便微信统一管理小程序能力。

### 高频追问

**为什么双线程架构反而导致 setData 有性能问题？**

因为逻辑层和渲染层不是同一个执行环境，数据更新需要经过通信和数据传输。如果一次传输的数据量很大，或者调用频率很高，就会产生明显开销。

---

## 3. 逻辑层和渲染层如何通信？

例如：

```js
this.setData({
  name: '张三'
})
```

可以理解为：

```text
JavaScript
   ↓
setData
   ↓
数据序列化
   ↓
Native
   ↓
渲染层
   ↓
页面更新
```

因此 `setData` 并不是普通 JavaScript 对象赋值。

### 面试重点

> setData 的性能问题本质上与逻辑层和渲染层之间的数据通信成本有关。

---

## 4. 小程序有哪些生命周期？

可以分为：

```text
App 生命周期
Page 生命周期
Component 生命周期
```

### App 生命周期

```js
App({
  onLaunch() {},
  onShow() {},
  onHide() {},
  onError() {}
})
```

- `onLaunch`：小程序初始化
- `onShow`：进入前台
- `onHide`：进入后台
- `onError`：发生错误

### Page 生命周期

```js
Page({
  onLoad() {},
  onShow() {},
  onReady() {},
  onHide() {},
  onUnload() {}
})
```

常见理解：

```text
onLoad   页面加载
   ↓
onShow   页面显示
   ↓
onReady  页面首次渲染完成
```

---

## 5. onLoad、onShow、onReady 有什么区别？

### onLoad

页面第一次加载时执行。

适合：

- 获取路由参数
- 初始化数据
- 发起页面首次请求

```js
onLoad(options) {
  console.log(options.id)
}
```

### onShow

页面显示时执行。

例如：

```text
A → B → 返回 A
```

返回 A 时，A 的 `onShow` 会再次触发。

适合：

- 页面重新获取数据
- 刷新页面状态

### onReady

页面首次渲染完成后触发。

适合：

- 获取节点
- 初始化 Canvas
- 创建 Observer

### 口诀

```text
onLoad：页面创建
onShow：页面显示
onReady：首次渲染完成
onHide：页面隐藏
onUnload：页面销毁
```

---

## 6. 页面生命周期执行顺序是什么？

首次进入页面，可以重点记忆：

```text
App.onLaunch
    ↓
App.onShow
    ↓
Page.onLoad
    ↓
Page.onShow
    ↓
Page.onReady
```

从其他页面返回时，通常重点关注：

```text
Page.onShow
```

页面真正销毁时：

```text
Page.onUnload
```

---

# setData 高频面试题

## 7. setData 的原理是什么？

例如：

```js
this.setData({
  name: '张三'
})
```

大致流程：

```text
修改页面数据
      ↓
setData
      ↓
逻辑层
      ↓
数据通信
      ↓
渲染层
      ↓
页面更新
```

因为存在跨层通信，所以 `setData` 不是免费的。

---

## 8. 为什么不能频繁调用 setData？

例如：

```js
setInterval(() => {
  this.setData({
    x: Math.random()
  })
}, 1)
```

会导致：

- JavaScript 执行频繁
- 数据序列化频繁
- 逻辑层与渲染层通信频繁
- 页面更新频繁
- CPU 和内存压力增加
- 页面出现掉帧和卡顿

### 优化原则

```text
减少调用次数
+
减少单次数据量
+
减少不必要的数据更新
```

---

## 9. 如何优化 setData？

### 方式一：批量更新

不推荐：

```js
this.setData({ a: 1 })
this.setData({ b: 2 })
this.setData({ c: 3 })
```

推荐：

```js
this.setData({
  a: 1,
  b: 2,
  c: 3
})
```

### 方式二：只更新变化字段

例如：

```js
this.setData({
  'user.age': 20
})
```

避免每次传递完整对象。

### 方式三：不要把非页面数据全部放进 data

例如缓存：

```js
this.cache = {}
```

不一定需要：

```js
data: {
  cache: {}
}
```

### 方式四：减少超大列表整体更新

不要频繁把几千条数据整体通过 `setData` 传递。

---

# 事件与通信

## 10. bind 和 catch 有什么区别？

```xml
<view bindtap="handleTap"></view>
```

事件执行后可以继续冒泡。

而：

```xml
<view catchtap="handleTap"></view>
```

可以阻止事件继续冒泡。

例如：

```xml
<view bindtap="parent">
  <view bindtap="child">
    点击
  </view>
</view>
```

点击子元素后：

```text
child
 ↓
parent
```

如果子元素使用 `catchtap`，则可以阻止继续冒泡。

---

## 11. dataset 是什么？

可以通过 `data-*` 给节点附加数据。

```xml
<button
  bindtap="handleClick"
  data-id="{{item.id}}"
>
  点击
</button>
```

JavaScript：

```js
handleClick(e) {
  console.log(e.currentTarget.dataset.id)
}
```

这里：

```text
data-id
   ↓
dataset.id
```

常用于列表操作，例如删除、编辑、查看详情。

---

## 12. 小程序页面之间如何通信？

常见方式：

### ① URL 参数

```js
wx.navigateTo({
  url: '/pages/detail/index?id=100'
})
```

获取：

```js
onLoad(options) {
  console.log(options.id)
}
```

适合简单参数。

### ② getApp / globalData

```js
const app = getApp()
app.globalData.user = user
```

适合简单全局状态。

### ③ Storage

```js
wx.setStorageSync('user', user)
```

适合持久化数据。

### ④ EventChannel

适合页面之间进行事件通信。

### ⑤ 状态管理

大型项目可以使用统一 Store。

---

# 组件通信

## 13. 父子组件如何通信？

### 父 → 子：properties

父：

```xml
<my-component user="{{user}}" />
```

子：

```js
Component({
  properties: {
    user: Object
  }
})
```

### 子 → 父：triggerEvent

子：

```js
this.triggerEvent('change', {
  value: 100
})
```

父：

```xml
<my-component bind:change="handleChange" />
```

### 获取子组件实例

```js
const child = this.selectComponent('#child')
child.someMethod()
```

### 面试总结

> 父子组件通信主要使用 properties 和 triggerEvent。父组件通过 properties 向子组件传值，子组件通过 triggerEvent 向父组件派发事件。

---

# 登录鉴权

## 14. 微信小程序登录流程是什么？

经典流程：

```text
小程序
   │
   │ wx.login()
   ↓
code
   │
   ↓
业务服务器
   │
   │ code
   ↓
微信服务器
   │
   ↓
openid / session_key
   │
   ↓
业务服务器
   │
   ↓
生成业务 Token
   │
   ↓
小程序
```

前端：

```js
wx.login({
  success(res) {
    const code = res.code

    wx.request({
      url: '/api/login',
      method: 'POST',
      data: { code }
    })
  }
})
```

后端根据 `code` 与微信服务端完成身份换取和校验，然后建立自己的登录态。

### 重点

不要把微信身份标识简单等同于业务 Token。

---

## 15. 为什么不能直接把 openid 当 Token？

`openid` 主要用于标识用户身份。

业务 Token 还应该承担：

- 登录态管理
- 过期时间
- 权限控制
- 服务端校验
- 注销
- 刷新等职责

推荐：

```text
微信身份
   ↓
服务端验证
   ↓
业务用户
   ↓
生成业务 Token / Session
   ↓
客户端保存登录态
```

---

# 网络请求

## 16. 小程序网络请求有什么限制？

主要注意：

### ① 合法域名

生产环境的请求域名需要按照微信小程序要求进行配置。

### ② HTTPS

生产环境通常使用 HTTPS。

### ③ 不同能力对应不同域名配置

例如：

- request
- uploadFile
- downloadFile
- WebSocket

需要按照对应能力配置。

---

## 17. 如何封装小程序网络请求？

可以使用 Promise 封装：

```js
function request(options) {
  return new Promise((resolve, reject) => {
    wx.request({
      ...options,

      success(res) {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else {
          reject(res)
        }
      },

      fail(err) {
        reject(err)
      }
    })
  })
}

export default request
```

实际项目还应该统一处理：

```text
Base URL
Token
请求头
Loading
错误码
登录过期
请求重试
重复请求
网络异常
```

---

# 分包

## 18. 什么是小程序分包？

大型小程序如果所有页面全部放在主包中，会导致首次加载资源较多。

可以将业务拆分：

```text
主包
 ├── 首页
 ├── 公共代码
 └── 核心页面

分包 A
 └── 商品模块

分包 B
 └── 用户模块
```

示例：

```json
{
  "pages": [
    "pages/index/index"
  ],
  "subpackages": [
    {
      "root": "packageA",
      "pages": [
        "pages/detail/index"
      ]
    }
  ]
}
```

### 好处

减少首次加载资源，提高启动体验。

---

## 19. 什么是独立分包？

独立分包可以相对独立地承载业务页面。

典型场景：

- 营销活动
- 推广页面
- 临时活动
- 从外部入口直接进入的业务

核心思想：

```text
用户进入活动页面
      ↓
优先加载活动相关资源
```

---

## 20. 什么是分包预下载？

假设：

```text
当前：首页
下一步：商品详情
```

可以提前下载商品相关分包：

```text
用户浏览首页
    ↓
后台预下载商品分包
    ↓
用户点击商品
    ↓
更快进入详情
```

适合：

- 用户路径稳定
- 下一页面访问概率高

但不要无脑预下载大量资源，否则可能增加网络压力。

---

# 性能优化

## 21. 小程序性能优化有哪些？

可以从五个方面回答：

```text
网络
↓
包体积
↓
数据通信
↓
渲染
↓
资源
```

### 网络

- 请求并行
- 减少重复请求
- 数据缓存
- CDN
- 接口合并
- 分页加载

### 包体积

- 分包
- 独立分包
- 删除无用资源
- 压缩资源

### setData

- 减少调用次数
- 减少数据量
- 批量更新
- 避免传递大对象
- 避免频繁更新列表

### 渲染

- 长列表优化
- 图片懒加载
- 减少复杂 WXML
- 减少不必要节点
- 避免频繁创建销毁

### 图片

- WebP 等现代格式
- CDN
- 缩略图
- 图片压缩
- 懒加载

---

## 22. 如何解决小程序首屏白屏？

先分析原因：

```text
主包过大
接口请求慢
首屏数据过大
图片过大
setData 数据量大
JavaScript 计算复杂
```

优化：

```text
分包
  ↓
首屏资源精简
  ↓
接口并行
  ↓
缓存数据
  ↓
骨架屏
  ↓
图片懒加载
  ↓
减少 setData
```

面试时最好结合项目说明：

> 我们当时发现首页首屏接口较多，并且首页列表一次性返回大量数据。后来将接口分成首屏核心接口和非核心接口，核心数据优先渲染，非核心数据延迟加载，同时对列表分页和图片进行优化，减少首屏数据量。

---

# 长列表

## 23. 小程序长列表如何优化？

错误：

```text
10000 条数据
     ↓
一次全部渲染
```

优化：

```text
10000 条
   ↓
第一次 20 条
   ↓
触底
   ↓
加载下一页
```

可以使用：

```js
onReachBottom() {
  this.loadMore()
}
```

同时结合：

- 分页
- 虚拟列表
- 图片懒加载
- 减少复杂节点
- 减少单次 setData 数据量

---

# 条件渲染

## 24. wx:if 和 hidden 有什么区别？

### wx:if

```xml
<view wx:if="{{show}}">
  内容
</view>
```

条件变化时，节点可能经历创建和销毁。

适合：

```text
不频繁切换
```

### hidden

```xml
<view hidden="{{!show}}">
  内容
</view>
```

主要控制显示隐藏，节点仍然存在。

适合：

```text
频繁切换
```

### 面试总结

> wx:if 更偏向条件性创建和销毁，hidden 更偏向已有节点的显示隐藏。需要根据切换频率和节点成本选择。

---

# Canvas

## 25. 小程序 Canvas 为什么会模糊？

常见原因是：

```text
CSS 尺寸
```

和：

```text
Canvas 实际像素尺寸
```

不匹配。

例如设备：

```text
CSS：375px
DPR：3
```

实际绘制像素可以达到：

```text
1125px
```

如果只按照 375px 的实际画布尺寸绘制，就可能出现模糊。

可以根据设备像素比进行适配：

```js
const dpr = wx.getSystemInfoSync().pixelRatio

canvas.width = width * dpr
canvas.height = height * dpr
```

然后根据绘图 API 对坐标系进行适当缩放。

---

# rpx

## 26. rpx 是什么？

`rpx` 是小程序提供的响应式尺寸单位。

经典规则：

```text
750rpx ≈ 屏幕宽度
```

例如：

```text
屏幕宽度 375px

750rpx ≈ 375px

1rpx ≈ 0.5px
```

因此：

```css
width: 375rpx;
```

可以根据不同设备宽度进行适配。

---

# WXML

## 27. WXML 和 HTML 有什么区别？

WXML 是小程序的页面描述语言。

HTML 是浏览器标准页面标记语言。

例如：

```xml
<view></view>
<text></text>
<image></image>
```

对应 Web 中经常见到：

```html
<div></div>
<span></span>
<img />
```

### 核心区别

小程序不能像传统 Web 那样：

```js
document.querySelector()
```

直接操作页面 DOM。

因为小程序的逻辑层和渲染层是分离的。

---

# 状态管理

## 28. 小程序如何进行状态管理？

小型项目：

```text
Page data
+
Component data
+
globalData
```

中大型项目：

```text
统一 Store
```

可以使用：

- MobX
- Redux 类方案
- 自定义 Store
- 项目框架自带状态管理

推荐思路：

```text
UI
 ↓
Action
 ↓
Store
 ↓
API
 ↓
Store
 ↓
UI
```

核心目标是避免：

```text
页面 A 保存一份
页面 B 保存一份
页面 C 又保存一份
```

导致状态不一致。

---

# 微信支付

## 29. 微信小程序支付流程是什么？

经典流程：

```text
小程序
   ↓
业务服务器创建订单
   ↓
微信支付服务
   ↓
返回支付参数
   ↓
小程序 wx.requestPayment
   ↓
用户支付
   ↓
微信支付
   ↓
服务端支付通知
   ↓
业务服务器更新订单状态
```

前端：

```js
wx.requestPayment({
  timeStamp,
  nonceStr,
  package,
  signType,
  paySign
})
```

### 高频追问

为什么不能只依赖前端支付成功回调？

因为客户端结果不能作为最终订单状态的唯一可信来源。

实际业务通常需要：

```text
微信支付服务端通知
        ↓
业务服务器
        ↓
订单状态确认
```

同时要考虑：

- 幂等
- 重复通知
- 支付超时
- 订单状态机
- 异常补偿

---

# 线上问题

## 30. 如何处理小程序线上高频问题？

可以从几个典型问题回答。

### ① 重复请求

前端：

```text
防抖
节流
请求锁
按钮 loading
```

后端：

```text
幂等 Token
业务唯一 ID
数据库唯一索引
```

### ② 重复提交订单

不能只依赖前端按钮禁用。

应该：

```text
客户端防重复
       +
服务端幂等
```

### ③ 页面卡顿

重点排查：

```text
setData 过于频繁
↓
单次数据量过大
↓
长列表
↓
图片过多
↓
复杂 WXML
↓
复杂 JavaScript 计算
```

### ④ 内存持续增长

排查：

```text
定时器没有清理
事件监听没有清理
WebSocket 没有关闭
全局缓存过大
页面缓存过多
```

例如：

```js
onUnload() {
  clearInterval(this.timer)

  if (this.socket) {
    this.socket.close()
  }
}
```

---

# 面试速记版

## Top 30

```text
1. 小程序双线程架构是什么？
2. 为什么采用双线程架构？
3. 逻辑层和渲染层如何通信？
4. 小程序有哪些生命周期？
5. onLoad、onShow、onReady 区别？
6. 生命周期执行顺序？
7. setData 原理是什么？
8. 为什么不能频繁 setData？
9. 如何优化 setData？
10. bind 和 catch 区别？
11. dataset 是什么？
12. 页面之间如何通信？
13. 父子组件如何通信？
14. 微信小程序登录流程？
15. 为什么不能直接使用 openid 当 Token？
16. 小程序网络请求有哪些限制？
17. 如何封装 request？
18. 什么是分包？
19. 什么是独立分包？
20. 什么是分包预下载？
21. 小程序性能如何优化？
22. 如何解决首屏白屏？
23. 长列表如何优化？
24. wx:if 和 hidden 区别？
25. Canvas 为什么模糊？
26. rpx 原理是什么？
27. WXML 和 HTML 区别？
28. 小程序如何做状态管理？
29. 微信支付流程？
30. 如何处理小程序线上高频问题？
```

# 面试重点优先级

如果时间有限，建议按照下面顺序准备：

```text
★★★★★ 双线程架构
★★★★★ setData 原理和优化
★★★★★ 生命周期
★★★★★ 性能优化
★★★★★ 登录鉴权
★★★★★ 页面/组件通信
★★★★★ 分包
★★★★★ 长列表
★★★★☆ 网络请求封装
★★★★☆ 微信支付
★★★★☆ Canvas
★★★☆☆ 状态管理
★★★☆☆ WebSocket
```

# 最值得重点背熟的 5 道题

### 第一题：为什么小程序采用双线程？

一定要能回答：

```text
安全
稳定
逻辑层与渲染层隔离
Native 负责能力和通信
```

### 第二题：setData 为什么会影响性能？

一定要回答：

```text
跨层通信
+
数据序列化
+
数据量
+
调用频率
```

### 第三题：你做过哪些性能优化？

最好使用：

```text
问题
 ↓
定位
 ↓
方案
 ↓
结果
```

来回答。

### 第四题：小程序登录流程？

一定要能画出：

```text
wx.login
 ↓
code
 ↓
服务端
 ↓
微信服务
 ↓
openid/session_key
 ↓
业务 Token
```

### 第五题：小程序支付如何保证订单最终一致？

重点回答：

```text
客户端支付
+
微信服务端通知
+
服务端订单状态机
+
幂等
+
异常补偿
```

---

# 总结

微信小程序面试并不只是考 API。

中高级岗位真正容易被追问的是：

```text
小程序架构
    ↓
为什么这样设计
    ↓
通信成本
    ↓
setData 性能
    ↓
页面渲染
    ↓
网络优化
    ↓
分包
    ↓
线上问题
```

如果是有实际项目经验的候选人，回答时不要只说“是什么”，最好采用：

```text
原理
 ↓
问题
 ↓
解决方案
 ↓
项目实践
 ↓
最终效果
```

这样的方式，面试表现会明显比单纯背 API 更好。
