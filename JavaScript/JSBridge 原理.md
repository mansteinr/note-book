

### JSBridge 的起源

>JSBridge 是一种 JS 实现的 Bridge，连接着桥两端的 Native 和 H5。它在 APP 内方便地让 Native 调用 JS，JS 调用 Native，是双向通信的通道。JSBridge 主要提供了 JS 调用 Native 代码的能力，实现原生功能如查看本地相册、打开摄像头、指纹支付等

#### H5 与 Native 对比

|       | H5 | Native |
| ----- | ----------- | --- |
| 稳定性 | 调用系统浏览器内核，稳定性较差 | 使用原生内核，更加稳定 |
| 灵活性 | 版本迭代快，上线灵活  |  迭代慢，需要应用商店审核，上线速度受限制   | 
| 网速影响 | 较大 |  较小   | 
| 流畅度 | 有时加载慢，给用户“卡顿”的感觉  |  加载速度快，更加流畅   | 
| 体验 | 功能受浏览器限制，体验有时较差  |  原生系统 api 丰富，能实现的功能较多，体验较好   | 
| 移植性 | 兼容跨平台跨系统，如 PC 与 移动端，iOS 与 Android  |  可移植性较低，对于 iOS 和 Android 需要维护两套代码   | 

### JSBridge 的双向通信原理
- ##### JS 调用 Native
  JS 调用 Native 的实现方式较多，主要有拦截 URL Scheme 、重写 prompt 、注入 API 等方法。

  - ###### 拦截 URL Scheme
    Android 和 iOS 都可以通过拦截 URL Scheme 并解析 Scheme 来决定是否进行对应的 Native 代码逻辑处理。

    Android 的话，Webview 提供了 shouldOverrideUrlLoading 方法来提供给 Native 拦截 H5 发送的 URL Scheme 请求。代码如下：

    <pre'>
    public class CustomWebViewClient extends WebViewClient {@Overridepublic boolean shouldOverrideUrlLoading(WebView view, String url) {  ......// 场景一：拦截请求、接收 schemeif (url.equals("xxx")) {// handle       ...// callback       view.loadUrl("javascript:setAllContent(" + json + ");")return true;     }return super.shouldOverrideUrlLoading(url);   }}
    </code>