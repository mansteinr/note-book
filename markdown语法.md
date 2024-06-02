
<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [语法](#语法)
- [My Great Heading](#custom-id)
- [目录生成](#目录生成)

<!-- /code_chunk_output -->

- [语法](#语法)
- [My Great Heading {#custom-id}](#my-great-heading-custom-id)
- [目录生成](#目录生成)

### 语法
[markdown官网](https://markdown.p2hp.com/getting-started/)
<link id="myCss" rel="stylesheet" type="text/css" href="./style.css">


<div style="background-color: #FFFF00;">
这里的文本将会有黄色背景。
</div>
d
<div></div>

> Dorothy followed her through many of the beautiful rooms in her castle.


```
{
  "firstName": "John",
  "lastName": "Smith",
  "age": 25
}
```

```json
{
  "firstName": "John",
  "lastName": "Smith",
  "age": 25
}
```

### My Great Heading {#custom-id}

<div id="custom-id">wrwe</div>


[甘特图](https://www.runoob.com/markdown/md-advance.html)
```mermaid
%% 语法示例
        gantt
        dateFormat  YYYY-MM-DD
        title 软件开发甘特图
        section 设计
        需求                      :done,    des1, 2014-01-06,2014-01-08
        原型                      :active,  des2, 2014-01-09, 3d
        UI设计                     :         des3, after des2, 5d
    未来任务                     :         des4, after des3, 5d
        section 开发
        学习准备理解需求                      :crit, done, 2014-01-06,24h
        设计框架                             :crit, done, after des2, 2d
        开发                                 :crit, active, 3d
        未来任务                              :crit, 5d
        耍                                   :2d
        section 测试
        功能测试                              :active, a1, after des3, 3d
        压力测试                               :after a1  , 20h
        测试报告                               : 48h
```

### 目录生成

  将光标移至需要插入目录的位置，可以通过Ctrl-Shift-P然后选择Generate Toc for markdown，目录即自动插入。 显示效果如下：