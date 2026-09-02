# Vite 打包优化指南

## 一、Vite 打包优化的核心目标

Vite 的打包优化主要解决以下问题：

```text
开发构建：
启动速度快
依赖预构建快
模块热更新快

生产构建：
包体积更小
加载速度更快
缓存命中率更高
首屏加载更快
浏览器兼容性更好
```

核心目标可以总结为：

> **减少构建时间、减少最终产物体积、提高资源缓存能力、按需加载代码。**

---

# 二、生产环境关闭 SourceMap

生产环境通常不需要生成 SourceMap：

```ts
// vite.config.ts
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    sourcemap: false
  }
})
```

生成 SourceMap：

```text
dist
├── app.js
└── app.js.map
```

`.map` 文件可能比较大。

生产环境：

```text
sourcemap: false
```

可以减少：

```text
打包时间
+
dist 文件体积
```

如果需要线上排查问题，可以考虑：

```text
SourceMap
↓
上传到错误监控平台
↓
不暴露给普通用户
```

---

# 三、关闭生产环境 Console

可以使用 `esbuild`：

```ts
export default defineConfig({
  esbuild: {
    drop: ['console', 'debugger']
  }
})
```

打包前：

```ts
console.log('用户信息', user)

debugger
```

打包后：

```text
自动删除
```

优点：

```text
减少生产代码
+
避免暴露调试信息
```

如果只是想删除部分日志，可以使用：

```ts
esbuild: {
  drop: ['debugger']
}
```

---

# 四、开启 Tree Shaking

Tree Shaking 的作用：

> **删除没有被使用的代码。**

例如：

```ts
export function add(a, b) {
  return a + b
}

export function subtract(a, b) {
  return a - b
}
```

项目中：

```ts
import { add } from './math'
```

生产构建：

```text
add        保留
subtract   删除
```

Vite 生产构建底层使用：

```text
Rollup
```

支持较好的 Tree Shaking。

---

## 推荐 ES Module

推荐：

```ts
import { debounce } from 'lodash-es'
```

避免：

```ts
import _ from 'lodash'
```

或者：

```ts
import debounce from 'lodash/debounce'
```

这样可以减少无用代码。

---

# 五、代码分割 Code Splitting

Vite 使用 Rollup 可以进行代码分割。

例如：

```text
index.js
   │
   ├── Home
   ├── User
   ├── Order
   └── Dashboard
```

如果全部打进：

```text
app.js
```

用户访问首页时：

```text
首页代码
+
用户中心
+
订单
+
数据大屏
```

都会下载。

更好的方式：

```text
首页
↓
只加载首页代码
```

用户访问：

```text
/order
```

再加载：

```text
order.js
```

---

# 六、路由懒加载

Vue Router：

```ts
const routes = [
  {
    path: '/',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/user',
    component: () => import('@/views/User.vue')
  },
  {
    path: '/order',
    component: () => import('@/views/Order.vue')
  }
]
```

最终：

```text
dist
├── index.js
├── home.js
├── user.js
└── order.js
```

访问：

```text
/
```

只加载：

```text
首页需要的资源
```

这是前端项目非常重要的优化。

---

# 七、组件异步加载

重量级组件不要阻塞首屏。

例如：

```ts
import Chart from './Chart.vue'
```

如果 `Chart.vue` 引入了 ECharts：

```text
ECharts
+
Chart组件
```

都会进入首屏。

可以使用：

```ts
import { defineAsyncComponent } from 'vue'

const Chart = defineAsyncComponent(
  () => import('./Chart.vue')
)
```

这样：

```text
首页
↓
先加载核心内容
↓
需要图表时
↓
加载 Chart
```

适合：

```text
ECharts
地图
富文本编辑器
PDF预览
Excel
大型编辑器
```

---

# 八、手动分包 manualChunks

默认情况下，依赖可能全部打入较大的 Vendor 包。

可以：

```ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vue: ['vue', 'vue-router'],
          element: ['element-plus'],
          echarts: ['echarts']
        }
      }
    }
  }
})
```

最终：

```text
dist
├── vue.xxx.js
├── element.xxx.js
├── echarts.xxx.js
└── app.xxx.js
```

优点：

```text
第三方库独立缓存
+
业务代码更新不会影响 Vendor
```

例如：

```text
第一次：

下载：
vue.js
app.js
```

修改业务代码后：

```text
app.js 改变
vue.js 不变
```

浏览器：

```text
vue.js
↓
使用缓存

app.js
↓
重新下载
```

---

# 九、合理拆分 Vendor

不推荐：

```ts
manualChunks: {
  vendor: [
    'vue',
    'vue-router',
    'element-plus',
    'echarts',
    'lodash'
  ]
}
```

因为：

```text
vendor.js
↓
非常大
```

更合理：

```ts
manualChunks: {
  vue: [
    'vue',
    'vue-router',
    'pinia'
  ],

  ui: [
    'element-plus'
  ],

  chart: [
    'echarts'
  ]
}
```

最终：

```text
vue.js
ui.js
chart.js
app.js
```

这样可以按需加载和缓存。

---

# 十、避免依赖全部打入 Vendor

例如：

```ts
import * as echarts from 'echarts'
```

可能导致较大的打包体积。

更合理的方式是按需引入：

```ts
import * as echarts from 'echarts/core'

import {
  LineChart
} from 'echarts/charts'

import {
  GridComponent,
  TooltipComponent
} from 'echarts/components'

import {
  CanvasRenderer
} from 'echarts/renderers'

echarts.use([
  LineChart,
  GridComponent,
  TooltipComponent,
  CanvasRenderer
])
```

原来：

```text
完整 ECharts
```

优化后：

```text
LineChart
+
必要组件
```

---

# 十一、图片资源优化

建议：

```text
PNG / JPG
↓
WebP / AVIF
```

例如：

```text
image.png

2MB
↓
WebP

500KB
```

还需要避免：

```text
页面显示：

800 × 600

实际图片：

8000 × 6000
```

应该根据实际显示尺寸提供图片。

---

# 十二、静态资源内联限制

Vite 可以配置：

```ts
export default defineConfig({
  build: {
    assetsInlineLimit: 4096
  }
})
```

含义：

```text
小于 4KB
↓
可能转成 Base64 内联
```

例如：

```text
logo.svg
↓
直接打进 JS/CSS
```

较大的文件：

```text
独立生成文件
```

例如：

```text
logo.png
image.webp
```

注意：

> 不建议盲目提高 `assetsInlineLimit`。

因为 Base64 会：

```text
增加 JS/CSS 文件大小
+
无法独立缓存
```

---

# 十三、使用 Brotli / Gzip

服务器可以对：

```text
JS
CSS
HTML
SVG
JSON
```

进行压缩。

原始：

```text
app.js

1MB
```

Gzip：

```text
约 300KB
```

Brotli：

```text
可能进一步减小
```

Nginx：

```nginx
gzip on;

gzip_types
  text/plain
  text/css
  application/javascript
  application/json
  image/svg+xml;
```

生产环境通常：

```text
静态资源
↓
Brotli
```

可以获得更好的压缩效果。

---

# 十四、预压缩

也可以构建时生成：

```text
app.js
app.js.gz
app.js.br
```

例如使用：

```text
vite-plugin-compression
```

配置示例：

```ts
import viteCompression from 'vite-plugin-compression'

export default defineConfig({
  plugins: [
    viteCompression({
      algorithm: 'brotliCompress'
    })
  ]
})
```

服务器根据浏览器：

```text
Accept-Encoding
```

选择：

```text
br
gzip
原始文件
```

---

# 十五、分析打包体积

推荐使用：

```text
rollup-plugin-visualizer
```

安装：

```bash
npm install rollup-plugin-visualizer -D
```

配置：

```ts
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig({
  plugins: [
    visualizer({
      open: true,
      filename: 'stats.html'
    })
  ]
})
```

打包：

```bash
npm run build
```

可以看到：

```text
dist

app.js
 ├── vue
 ├── lodash
 ├── echarts
 ├── element-plus
 └── business
```

重点检查：

```text
哪个依赖最大？
是否存在重复依赖？
是否有未使用的大型依赖？
是否存在错误的完整导入？
```

优化前不要盲目修改配置。

正确流程：

```text
Build
↓
Analyze
↓
找到大模块
↓
针对性优化
↓
再次 Build
↓
对比结果
```

---

# 十六、设置 Chunk Size Warning

可以配置：

```ts
export default defineConfig({
  build: {
    chunkSizeWarningLimit: 1000
  }
})
```

超过：

```text
1000KB
```

会产生警告。

注意：

```text
chunkSizeWarningLimit
```

只是：

> 修改警告阈值。

它：

```text
不会减少文件体积
```

所以不要简单通过：

```ts
chunkSizeWarningLimit: 5000
```

来“解决”打包体积过大的问题。

应该先：

```text
分析
↓
代码分割
↓
按需加载
↓
删除无用依赖
```

---

# 十七、外部化 External

一些资源不一定需要打进应用。

例如：

```text
大型 SDK
CDN 资源
```

可以配置：

```ts
build: {
  rollupOptions: {
    external: ['some-library']
  }
}
```

但是需要注意：

```text
external
```

之后：

> 需要确保运行环境能够找到这个模块。

常见方案：

```text
应用
  ↓
CDN
  ↓
第三方资源
```

例如：

```html
<script src="https://cdn.example.com/library.js"></script>
```

适合：

```text
大型稳定依赖
长期缓存
多项目共享依赖
```

---

# 十八、CSS 代码分割

Vite 默认支持 CSS Code Splitting。

可以配置：

```ts
export default defineConfig({
  build: {
    cssCodeSplit: true
  }
})
```

例如：

```text
Home.vue
↓
home.css

User.vue
↓
user.css
```

访问首页：

```text
加载 home.css
```

访问用户页面：

```text
再加载 user.css
```

如果关闭：

```ts
cssCodeSplit: false
```

可能：

```text
所有 CSS
↓
打成一个文件
```

一般 SPA 推荐：

```text
cssCodeSplit: true
```

---

# 十九、优化 CSS

可以：

```text
CSS
↓
删除未使用代码
↓
压缩
```

例如项目使用：

```text
Tailwind CSS
```

但最终只使用了一部分工具类。

应该：

```text
扫描实际使用内容
↓
删除无用 CSS
```

避免：

```text
完整 CSS Framework
↓
全部进入生产包
```

---

# 二十、优化构建目标 target

可以：

```ts
export default defineConfig({
  build: {
    target: 'es2020'
  }
})
```

浏览器兼容：

```text
现代浏览器
```

时，可以减少过多的：

```text
语法转换
Polyfill
```

但是：

> target 需要根据项目实际浏览器兼容范围配置。

不要为了减小体积随意提高 target。

---

# 二十一、动态导入

例如：

```ts
const module = await import('./heavy-module')
```

Vite 会生成：

```text
heavy-module.js
```

只有执行：

```ts
import()
```

才下载。

适合：

```text
导出 Excel
生成 PDF
代码编辑器
图表
AI 功能
大型算法模块
```

例如：

```ts
async function exportExcel() {
  const ExcelJS = await import('exceljs')

  // 导出 Excel
}
```

用户没有点击导出：

```text
ExcelJS
↓
不会下载
```

---

# 二十二、Vue 组件库按需引入

避免：

```ts
import ElementPlus from 'element-plus'

app.use(ElementPlus)
```

可以使用：

```text
unplugin-vue-components
```

实现：

```text
按需自动导入
```

这样：

```text
使用 ElButton
↓
只引入相关组件
```

而不是：

```text
整个 Element Plus
↓
全部进入 Bundle
```

---

# 二十三、避免重复依赖

例如：

```text
项目
├── lodash 4.17
├── dependency A
│   └── lodash 4.16
└── dependency B
    └── lodash 4.17
```

可能出现：

```text
多个相似版本
```

应该：

```text
pnpm dedupe
```

或者统一依赖版本。

使用：

```bash
pnpm why lodash
```

分析：

```text
为什么项目存在这个依赖？
谁依赖它？
是否可以删除？
```

---

# 二十四、依赖预构建 optimizeDeps

Vite 开发环境中使用：

```text
Dependency Pre-Bundling
```

主要目的是：

```text
优化 node_modules 依赖加载
```

例如：

```ts
export default defineConfig({
  optimizeDeps: {
    include: [
      'lodash-es'
    ]
  }
})
```

可以：

```text
预构建依赖
```

需要注意：

> `optimizeDeps` 主要优化开发环境启动和依赖加载，不是生产环境包体积优化的主要手段。

---

# 二十五、开发环境缓存

Vite 会缓存预构建依赖：

```text
node_modules/.vite
```

如果：

```text
依赖异常
```

可以清理：

```bash
rm -rf node_modules/.vite
```

然后重新启动：

```bash
npm run dev
```

---

# 二十六、预构建和生产构建的区别

很多人容易混淆：

```text
Vite
```

实际上：

```text
开发环境
↓
esbuild + Native ESM
```

生产环境：

```text
Rollup
↓
Bundle
↓
Code Splitting
↓
Tree Shaking
↓
Minify
```

可以理解：

```text
                Vite

开发环境                     生产环境

Dependency                  Rollup
Pre-Bundling                   │
    ↓                          ↓
esbuild                    Tree Shaking
    ↓                          ↓
快速启动                   Code Splitting
                               ↓
                           Minify
                               ↓
                            dist
```

---

# 二十七、生产环境推荐配置

一个比较常见的配置：

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    // 不生成 SourceMap
    sourcemap: false,

    // CSS 分割
    cssCodeSplit: true,

    // 压缩
    minify: 'esbuild',

    // 删除 console
    target: 'es2020',

    rollupOptions: {
      output: {
        manualChunks: {
          vue: [
            'vue',
            'vue-router',
            'pinia'
          ],

          element: [
            'element-plus'
          ]
        }
      }
    }
  },

  esbuild: {
    drop: [
      'console',
      'debugger'
    ]
  }
})
```

注意：

> 不建议直接复制所有 `manualChunks` 配置到项目中。

应该根据：

```text
实际依赖
实际页面
实际访问路径
Bundle 分析结果
```

进行拆包。

---

# 二十八、完整优化流程

推荐：

```text
① 打包
   ↓
② 分析 Bundle
   ↓
③ 找到最大文件
   ↓
④ 判断来源
   │
   ├── 第三方库过大
   ├── 页面代码过大
   ├── 图片过大
   ├── 重复依赖
   └── 没有按需加载
   ↓
⑤ 代码分割
   ↓
⑥ 路由懒加载
   ↓
⑦ 组件异步加载
   ↓
⑧ 依赖按需引入
   ↓
⑨ 图片压缩
   ↓
⑩ Brotli / CDN / 缓存
   ↓
再次分析 Bundle
```

---

# 二十九、Vite 打包优化面试题

## 1. Vite 如何进行 Tree Shaking？

Vite 生产环境使用 Rollup 打包，通过：

```text
ES Module 静态分析
```

判断：

```text
哪些模块被使用
哪些代码未被使用
```

从而删除未使用代码。

---

## 2. Vite 如何实现代码分割？

主要通过：

```ts
import()
```

动态导入：

```ts
const module = await import('./module')
```

以及：

```text
Vue Router
```

的懒加载。

Rollup 会生成独立的 Chunk。

---

## 3. manualChunks 有什么作用？

用于：

```text
手动控制代码分包
```

例如：

```text
Vue
UI组件库
图表库
业务代码
```

分别生成不同 Chunk。

主要目的：

```text
提高缓存利用率
+
减少业务代码和第三方依赖相互影响
```

---

## 4. 如何优化首屏包体积？

主要：

```text
路由懒加载
+
组件异步加载
+
Tree Shaking
+
第三方库按需引入
+
图片优化
+
删除无用依赖
+
分析 Bundle
```

---

## 5. optimizeDeps 是什么？

`optimizeDeps` 用于：

```text
开发环境依赖预构建
```

主要解决：

```text
CommonJS
+
大量小模块
```

在浏览器中加载效率较低的问题。

它不是生产环境主要打包优化手段。

---

# 三十、最终总结

Vite 打包优化可以总结成：

```text
                    Vite 打包优化
                         │
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
      减少体积          代码分割         缓存优化
        │                │                │
   Tree Shaking       路由懒加载        CDN
   删除依赖            动态 import       Hash
   按需引入            异步组件          长缓存
   图片压缩            manualChunks      独立 Vendor
   CSS优化
        │                │                │
        └────────────────┼────────────────┘
                         ↓
                     压缩资源
                         │
                  Gzip / Brotli
                         ↓
                      分析 Bundle
                         │
                rollup visualizer
                         ↓
                    持续针对性优化
```

最终可以记住一句话：

> **Vite 打包优化不是简单修改 `vite.config.ts`，而是先通过 Bundle 分析找到体积和加载瓶颈，再结合 Tree Shaking、代码分割、懒加载、依赖按需引入、压缩、缓存和 CDN 进行针对性优化。**

## 推荐优先级

实际项目可以按照下面顺序进行：

```text
第一优先级：
路由懒加载
+
删除无用依赖
+
第三方库按需引入

第二优先级：
组件异步加载
+
图片 WebP / AVIF
+
代码分割

第三优先级：
Brotli
+
CDN
+
HTTP 缓存

第四优先级：
manualChunks 精细分包
+
预加载
+
构建参数优化
```

> **先解决 5MB 的大问题，再解决 5KB 的小问题。优化应该基于数据，而不是盲目调整配置。**