# LangGraph Command 面试题集

> 考察 LangGraph `Command` 原语的概念、参数、场景与排障能力，共 6 题。

## 一、基础题

### Q1：Command 是什么？解决什么问题？
**考察点**：概念理解
Command 是控制图执行的核心原语，让节点返回时同时完成「状态更新 + 流程跳转」，替代「返回字典 + add_conditional_edges」的拆分写法，使动态决策代码更紧凑。

### Q2：Command 的四个参数各有什么作用？
**考察点**：参数掌握
- `update`：更新图状态（等同返回字典）
- `goto`：指定下一步跳转节点
- `graph`：子图跳父图（`Command.PARENT`）
- `resume`：中断后恢复执行的输入值

## 二、进阶题

### Q3：如何用 Command 实现人机协同（HITL）？
**考察点**：HITL 应用
```python
def node(state):
    d = interrupt({"amount": state["amount"]})
    return Command(update={"ok": d}, goto="exec")
# 外部恢复：graph.invoke(None, Command(resume="yes"))
```
interrupt 暂停并持久化，Command(resume=) 把决策注入回断点。

### Q4：子图中如何跳回父图节点？需注意什么？
**考察点**：子图与类型注解
用 `graph=Command.PARENT`。父图需用 `def call(s) -> Command[Literal["bob"]]:` 包装子图，否则可视化无法识别路由。

## 三、综合应用题

### Q5：滥用 Command(goto=...) 有什么问题？
**考察点**：最佳实践
把所有控制流塞进节点会导致路由不可视、难调试。应以边声明为主，Command goto 作为「例外」（错误恢复、HITL、动态交接）。

### Q6：Command 路由与静态边冲突时如何排查？
**考察点**：问题排查
Command 优先于静态边，同时存在时静态边被忽略。检查节点返回类型注解 `Command[Literal[...]]` 是否声明，否则图编译无法识别跳转目标，导致路由失效。

---

> **评分建议**：概念 20% / 参数 20% / HITL 25% / 子图 15% / 实践 20%。
