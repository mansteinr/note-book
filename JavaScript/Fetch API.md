### 简介
在JavaScript中，Fetch API提供了一个全局的fetch()方法，用于发起网络请求。它返回一个Promise，该Promise在接收到响应时resolve，但注意，即使响应状态码是404或500，Promise也不会reject，除非网络请求失败（如网络断开）

基本用法：
```
fetch(url)
  .then(response => {
    // 检查响应状态
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json(); // 解析JSON数据
  })
  .then(data => {
    console.log(data);
  })
  .catch(error => {
    console.error('There was a problem with the fetch operation:', error);
  });

```