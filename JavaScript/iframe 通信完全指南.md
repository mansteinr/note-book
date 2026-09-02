### 同源（不跨域）通信

#### 获取 iframe 内容
父页面 → iframe

```
const iframe = document.getElementById('myIframe');
const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;

// 读取 iframe 内容
console.log(iframeDoc.body.innerHTML);

// 修改 iframe 内容
iframeDoc.body.style.backgroundColor = 'red';
iframeDoc.querySelector('#title').textContent = '修改后的标题';
```

iframe → 父页面

```
// 在 iframe 内部
const parentDoc = window.parent.document;
const parentBody = window.parent.document.body;

// 访问父页面元素
console.log(parentDoc.getElementById('parentTitle').textContent);

// 修改父页面
parentDoc.body.style.backgroundColor = 'blue';
```


####  调用函数

父页面调用 iframe 函数
```
// iframe 内部定义函数
function sayHello(name) {
    return `Hello, ${name}!`;
}

// 父页面调用
const result = iframe.contentWindow.sayHello('World');
console.log(result); // "Hello, World!"
```

iframe 调用父页面函数
```
// 父页面定义函数
function parentFunction(data) {
    console.log('收到 iframe 数据:', data);
    return '父页面已处理';
}

// iframe 内部调用
const result = window.parent.parentFunction('来自 iframe 的消息');
console.log(result); // "父页面已处理"
```

###  共享变量

```
// 父页面
window.sharedData = { count: 0, user: 'Alice' };

// iframe 访问
console.log(window.parent.sharedData.user); // "Alice"
window.parent.sharedData.count++; // 修改共享数据
```


### 跨域通信

 postMessage API（推荐）

 ### 其他跨域方案

 document.domain（仅限子域不同）

 当两个页面主域名相同但子域不同时使用：

 比如：http://sub1.example.com 和 http://sub2.example.com 都可以使用 document.domain = 'example.com' 来实现跨域通信。

 ```
 // 两个页面都设置相同的 document.domain
document.domain = 'example.com';
// 之后就可以像同源一样操作了
```