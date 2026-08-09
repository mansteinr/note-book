1、load事件触发时，页面上所有的DOM，样式表，脚本，图片都已经加载完成了.

```
window.onload = function() {
    var span = document.querySelector("span");
    console.log(span,"onload");
};
```

2、DOMContentLoaded事件触发时，仅当DOM加载完成，不包括样式表，图片(譬如如果有async加载的脚本就不一定完成)

```
document.addEventListener("DOMConetentLoaded", function() {
    var span = document.querySelector("span");
    console.log(span, "DOMConetentLoaded");
});
```

当加载的脚本内容并不包含立即执行DOM操作时，使用onDOMContentLoaded事件是个更好的选择，会比onload事件执行时间更早。

