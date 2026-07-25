js 超过 16 位的整数，精度将开始丢失

```
import api from '@/api'
import JSONBig from 'json-bigint'
const host = window.config.service_login
export function login(data) {
  return api({
    data,
    method: 'post',
    url: host + '/oauth/token',
    transformResponse: [
      function(data) {
        try {
          // 前端兼容customerId精度丢失问题
          return JSONBig.parse(data)
        } catch (err) {
          return data
        }
      }
    ]
  })
}
```

axios 默认会自动做 JSON.parse ，这个逻辑就内置在默认的 transformResponse 里。


如果你写了 transformResponse ，就 完全覆盖 了默认的，axios 不会再自动 JSON.parse 。

## JSONBig.parse() 的作用
### 解决的问题：JS 大整数精度丢失
### 解决方法：使用 JSONBig.parse() 替代 JSON.parse()


```
// 后端返回的 customerId = 1234567890123456789（19位）
const data = '{"customerId": 1234567890123456789}'

// 原生 JSON.parse —— 精度丢失！
const obj1 = JSON.parse(data)
console.log(obj1.customerId)  // 1234567890123456800  ← 末尾变成 0 了，值变了！

// JSONBig.parse —— 精度保留
const obj2 = JSONBig.parse(data)
console.log(obj2.customerId)  // "1234567890123456789"  ← 字符串形式，完全正确
```


json-bigint 库在解析 JSON 时，遇到大整数不转成 Number ，而是转成 字符串 （或 BigNumber 对象），从而完整保留精度。

```
getAccessToken(data).then(async res => {
              // 这个toString 必须要 因为json-bigint插件的原因
              const id = res.id.toString()
              const customerId = res.customerId.toString()
              this.setInfo('id', id)
              this.setInfo('customerId', customerId)
              resolve(res)
            }).catch(async error => {
              console.log(error.message)
              reject(error)
            })
            ```