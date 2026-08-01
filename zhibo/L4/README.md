# CrewAI + DeepSeek + Bocha 协作示例

一个完全使用国产 AI 服务的 Multi-Agent 示例项目。两个 Agent 协作完成"调研 + 撰稿"任务,展示 CrewAI 框架的核心机制。

---

## 项目简介

本项目演示如何用 [CrewAI](https://www.crewai.com/) 框架搭建一个多智能体团队,所有外部服务都使用国内可访问的国产方案:

- **LLM**:DeepSeek API(`deepseek-reasoner` 推理 + `deepseek-chat` 对话)
- **搜索**:Bocha Web Search API(国产 Google 替代)
- **框架**:CrewAI(角色驱动的多 Agent 编排)

适合的场景:学习多 Agent 系统、快速搭建中文资料调研 Agent、国内合规部署的 AI 应用原型。

---

## 团队设计

项目里有两个 Agent,分工明确:

**研究员(Researcher)** 负责针对给定话题进行联网调研,搜集 5 个以上权威信息源,并整理成结构化笔记。使用 `deepseek-reasoner` 推理模型,因为筛选和判断信息源权威性需要较强的推理能力。配备 Bocha 搜索工具。

**撰稿人(Writer)** 接收研究员的笔记作为上下文,撰写一篇 800-1200 字的中文技术简报。使用 `deepseek-chat` 通用模型,因为写作任务对推理深度要求不高,用便宜的模型省成本。不配备工具。

两个 Agent 通过 CrewAI 的 `context=[research_task]` 机制实现协作 —— 研究员的产出会自动注入到撰稿人的 prompt 里。

---

## 快速开始

### 1. 申请 API Key

需要两个 key,都有免费额度:

| 服务 | 申请地址 | 免费额度 |
|------|---------|----------|
| DeepSeek | [platform.deepseek.com](https://platform.deepseek.com) | 新用户赠送额度 |
| Bocha | [open.bochaai.com](https://open.bochaai.com) | 注册即送 |

### 2. 安装依赖

```bash
pip install crewai requests
```

只需要这两个包,不需要 `crewai-tools`(因为我们自己实现了 Bocha 工具)。

> **环境要求**:Python 3.10 或以上。

### 3. 配置环境变量

Linux / macOS:

```bash
export DEEPSEEK_API_KEY="sk-..."
export BOCHA_API_KEY="sk-..."
```

Windows PowerShell:

```powershell
$env:DEEPSEEK_API_KEY="sk-..."
$env:BOCHA_API_KEY="sk-..."
```

或者放在 `.env` 文件里配合 `python-dotenv` 使用(推荐生产环境用法)。

### 4. 运行

```bash
python crewai_deepseek_bocha_example.py
```

终端会输出两个 Agent 的完整"思考过程",最后在当前目录生成 `briefing.md`。

### 5. 修改话题

默认调研的话题是"Multi-Agent 系统在 2026 年的工程实践"。要换话题,改最后那个 `kickoff()` 调用:

```python
result = crew.kickoff(
    inputs={"topic": "你的话题"}
)
```

---

## 代码结构

```
crewai_deepseek_bocha_example.py
├─ 1. Bocha 搜索工具类       (BochaSearchTool)
├─ 2. DeepSeek LLM 配置      (reasoner + chat 两个实例)
├─ 3. 工具实例化              (search_tool)
├─ 4. Agent 定义              (researcher + writer)
├─ 5. Task 定义               (research_task + writing_task)
├─ 6. Crew 组装               (sequential 顺序执行)
└─ 7. 启动入口                (前置检查 + kickoff)
```

整个文件约 150 行,结构清晰,适合作为学习模板。

---

## 工作原理

整个流程大致是这样运作的:

1. **kickoff 启动** —— `inputs` 里的 `{topic}` 变量被替换到 Task description 中。
2. **研究员上场** —— 进入 ReAct 循环:思考要搜什么 → 调用 Bocha 搜索 → 看结果 → 决定是否再搜 → 整理最终笔记。通常涉及 3-5 次 LLM 调用 + 2-4 次搜索调用。
3. **产出传递** —— 研究员的笔记通过 `context` 字段自动作为撰稿人的输入。
4. **撰稿人上场** —— 直接撰写,通常 1 次 LLM 调用即可输出 Markdown 简报。
5. **结果写盘** —— 写入 `briefing.md`,同时打印到终端。

完整一次运行大约消耗 **15-30K tokens**,在国内服务上费用大约几分到一两毛钱人民币。

---

## 成本估算

以一次完整运行为例(2026 年初的价格):

| 项目 | 用量 | 估算成本 |
|------|------|----------|
| DeepSeek Reasoner | 约 10K tokens | ¥0.10 - 0.20 |
| DeepSeek Chat | 约 5K tokens | ¥0.005 - 0.015 |
| Bocha 搜索 | 3-5 次 | ¥0.05 - 0.10 |
| **合计** | | **约 ¥0.15 - 0.35** |

跑 100 次实验大约 ¥15 - 35,比同等任务用 GPT-4o + Serper 便宜一个数量级。

---

## 常见问题

**Q:跑起来报 `DEEPSEEK_API_KEY` 未设置?**
A:确认环境变量在当前终端会话里。可以 `echo $DEEPSEEK_API_KEY` 验证一下。如果用 IDE 启动,记得在 IDE 的运行配置里也设上。

**Q:Agent 输出全是英文,我想要中文输出?**
A:检查 Task 的 `expected_output` 字段。代码里已经在撰稿人的 description 中明确"面向中文技术读者",通常会输出中文。如果还不行,在 Agent 的 `backstory` 里加一句"始终用中文回复"。

**Q:Bocha 返回结果太少 / 不够新?**
A:调整 `BochaSearchTool._run` 里的两个参数:把 `count` 从 10 调大(最大 50)、把 `freshness` 改成 `oneMonth` 或 `oneWeek` 限定时间范围。

**Q:研究员只搜了一次就出 Final Answer,质量不高?**
A:在研究员的 backstory 里加一句"对于复杂话题,至少进行 2-3 次搜索以确保覆盖全面"。LLM 在 ReAct 范式里会参考 backstory 决策行为。

**Q:跑到一半 token 用超了?**
A:研究员的 `max_iter=8` 限制了最多 8 次 ReAct 循环,如果觉得还是太多,改成 5。另外检查 `max_tokens=4000` 是否合理,可以调小。

**Q:能换成 GPT 或 Claude 吗?**
A:能。把 `LLM(model=...)` 里的 model 字符串换掉就行:`openai/gpt-4o`、`anthropic/claude-sonnet-4-5` 等。对应的 api_key 也要换。CrewAI 通过 LiteLLM 统一了不同厂商的接口。

**Q:能加更多 Agent 吗?比如再加个审查员?**
A:能,这正是 CrewAI 的优势。定义一个新的 Agent 和 Task,把 Task 的 `context` 设为 `[writing_task]`,然后加到 `Crew(agents=..., tasks=...)` 列表里即可。注意 token 消耗会显著增加。

**Q:能并行执行任务而不是顺序吗?**
A:CrewAI 的 `Process.sequential` 是顺序执行。如果想并行,改用 `Process.hierarchical`(Manager Agent 调度,会自动并行可并行的任务),但 Manager 本身也消耗 token,要权衡。

---

## 扩展方向

如果想进一步完善这个项目,几个常见的扩展方向:

**加网页正文抓取工具**。Bocha 返回的是摘要,有时候 Agent 需要读全文。可以加一个 `WebScraperTool`,让 Agent 在搜索后选定一两个最相关的链接,抓取正文做深度分析。

**多搜索源组合**。同时挂载 Bocha 和别的搜索工具(比如 ArxivTool 搜论文、GithubTool 搜代码),让 Agent 根据话题自己选用哪个。

**加输出审查 Agent**。在 writer 后面再串一个 reviewer,检查产出的事实准确性、引用规范性,把不合格的内容打回重写。这就形成了一个三人协作的流水线。

**接入向量数据库**。让研究员先搜本地知识库(企业内部资料),再决定要不要联网搜公开资料。CrewAI 可以挂载 RAG 工具如 `PGSearchTool`。

**部署成 API**。把 `kickoff` 包成 FastAPI 接口,前端传话题,后端返回简报,就是一个完整的"AI 写稿服务"。

**导出更丰富的格式**。把 `output_file="briefing.md"` 改成调用 Pandoc 等工具,直接生成 PDF 或 Word。

---

## 相关资源

- CrewAI 官方文档:https://docs.crewai.com/
- CrewAI GitHub:https://github.com/crewAIInc/crewAI
- DeepSeek API 文档:https://api-docs.deepseek.com/zh-cn/
- Bocha API 文档:https://bocha-ai.feishu.cn/wiki/RXEOw02rFiwzGSkd9mUcqoeAnNK
- LiteLLM 支持的模型列表:https://docs.litellm.ai/docs/providers

---

## 许可

本示例代码仅供学习使用。注意各 API 服务的使用条款:

- DeepSeek API:遵循 DeepSeek 服务协议
- Bocha API:遵循 Bocha 服务协议
- CrewAI:Apache 2.0 协议

在生产环境使用时,请关注各服务的数据合规要求和速率限制。
